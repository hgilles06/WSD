#!/usr/bin/env python

'''
    Tried to implemented Porter Stemming Algorithm aka Suffix stripping algorithm
'''

#import nltk
import re
import sys

class StemWord:

    def __init__(self):
        self.stem = []

    def step_1a(self, word):
        '''
            Rules for 1a:
                SSES -> SS
                IES -> I
                SS -> SS
                S ->
        '''

        # must not have space between word and |
        # * is greedy and ?* is non greedy
        # result is list of tuple
        result = re.findall(r'^(.*?)(SSES|IES|SS|S)$', word)

        if len(result) == 0:
            return word

        stem = result[0][0]
        suffix = result[0][1]

        if (suffix == 'SSES'):
            stem = stem + 'SS'
        elif ( suffix == 'IES'):
            stem = stem + 'I'
        elif ( suffix == 'SS'):
            stem = stem + 'SS'
        elif ( suffix == 'S'):
            if (stem == 'GOE' or stem =='DOE'):
                stem = stem[:2]
            elif(stem == 'HI'):
                stem = stem+'S'
            stem = stem
        else:
            #print >> sys.stderr, 'No mapping found in step 1a'
            pass
        return stem

    def step_1b(self, word):
        '''
            rules for 1b
                1. (m > 0) EED -> EE
                2. (*v*) ED ->
                3. (*v*) ING ->
                4. (*d and not (*L or *S or *Z)) -> single letter
                5. (m=1 and *o) -> E
        '''

        consonant_vowel_dict = self.to_consonant_vowel(word)
        #print >> sys.stderr, consonant_vowel_dict

        # which rule does the word map to ??
        result = re.findall(r'^(.*?)(EED|ED|ING)$', consonant_vowel_dict.keys()[0])

        if len(result) == 0:
            return word
        # reduced stem
        ret_word = ''

        # check if the second or third rules were applies
        second_or_third = False

        # to get the consonant and vowel of stem
        stem_consonant = (self.to_consonant_vowel(result[0][0])).values()[0]
        #print stem_consonant

        # get the count of VC in stem
        str_to_count = 'VC'
        m = stem_consonant.count(str_to_count)
        #print m

        # case maps to (m > 0) EED -> EE
        if ( (m > 0) and (result[0][1] == 'EED') ):
            return result[0][0]+'EE'
        # case maps to (*v*) ED -> null
        elif ( result[0][1] == 'ED'):
            if ( stem_consonant.count('V') > 0 ):
                ret_word = result[0][0]
                second_or_third = True
        # case maps to (*v*) ING -> null
        elif ( result[0][1] == 'ING' ):
            if ( stem_consonant.count('V') > 0 ):
                ret_word = result[0][0]
                second_or_third = True
        else:
            #print >> sys.stderr, 'No matching found in step 1b'
            pass

        if (second_or_third is not True):
            return word

        #case with AT -> ATE
        #print >> sys.stderr, 'rule_123 ...'
        rule_123 = re.findall(r'^(.*?)(AT|BL|IZ)$', ret_word)
        #print >> sys.stderr, rule_123

        if ( len(rule_123) == 0 ):
            #print >> sys.stderr, 'go to rule 4'
            pass
        elif ( rule_123[0][1] == 'AT' ):
            return rule_123[0][0] + 'ATE'
        elif( rule_123[0][1] == 'BL'):
            return rule_123[0][0] + 'BLE'
        elif( rule_123[0][1] == 'IZ'):
            return rule_123[0][0] + 'IZE'

        # Have to check the consecuive pair of letter
        # [a-z]*([a-z])\1([a-z])\2[a-z]*  regex using back reference
        rule_4 = re.findall(r'^(.*?)(AA|BB|CC|DD|EE|FF|GG|HH|II|JJ|KK|LL|MM|NN|OO|PP|QQ|RR|SS|TT|UU|VV|WW|XX|YY|ZZ)$', ret_word)

        if (len(rule_4) ==0 ):
            #print >> sys.stderr, 'No matching for rule 4'
            pass
        elif ( (len(rule_4) > 0) and ((rule_4[0][1] != 'LL') and (rule_4[0][1] != 'SS') and (rule_4[0][1] != 'ZZ'))):
            #print >> sys.stderr, rule_4[0][1]
            return rule_4[0][0] + rule_4[0][1][0]

        # rule5: (m=1 and *o) -> E
        # *o means stem ends in cvc where second c is not W,X,Y
        # Have to distinguish between cvc and CVC because C is ccc.. length > 0
        stem = self.to_consonant_vowel(ret_word, True)

        rule_5 = re.findall(r'^(.*?)(CVC)$', stem.values()[0])
        #print >> sys.stderr, rule_5

        if ( len(rule_5) > 0 ):
            # reduce the consonant_vowel
            norm_list = self.normalize_list(stem.values()[0])
            #print >> sys.stderr, norm_list
            m = (''.join(norm_list)).count('VC')
            if ( m == 1):
                ret_word = stem.keys()[0] + 'E'
            else:
                ret_word = ret_word
        else:
            return ret_word

        return ret_word

    def step_1c(self, word):
        '''
            rule
                1) (*v*) Y -> I  # stem contains vowel, word ends in Y
        '''
        # TODO: Implement step_1c
        rule_1 = re.findall(r'^(.*?)(Y)$', word)
        if (len(rule_1) == 0):
            return word

        stem_str = rule_1[0][0]
        stem_consonant = self.to_consonant_vowel(stem_str)
        #print stem_consonant

        if ( (stem_consonant.values()[0]).count('V') > 0):
            return stem_consonant.keys()[0] + 'I'
        else:
            return word

    def step_2(self, word):
        '''
            Rules:
            (m > 0) ATIONAL -> ATE
            (m > 0) TIONAL -> TION

            (m > 0) ENCI -> ENCE
            (m > 0) ANCI -> ANCE
            (m > 0) IZER -> IZE
            (m > 0) ABLI -> ABLE
            (m > 0) ALLI -> AL
            (m > 0) ENTLI -> ENT
            (m > 0) ELI -> E
            (m > 0) OUSLI -> OUS
            (m > 0) IZATION -> IZE
            (m > 0) ATION -> ATE
            (m > 0) ATOR -> ATE
            (m > 0) ALISM -> AL
            (m > 0) IVENESS -> IVE
            (m > 0) FULNESS -> FUL
            (m > 0) OUSNESS -> OUS
            (m > 0) ALITI -> AL
            (m > 0) IVITI -> IVE
            (m > 0) BILITI -> BLE
        '''
        count = False
        parse_stem = re.findall(r'^(.*?)(ATIONAL|TIONAL|ENCI|ANCI|IZER|ABLI|ALLI|ENTLI|ELI|OUSLI|IZATION|ATION|ATOR|ALISM|IVENESS|FULNESS|OUSNESS|ALITI|IVITI|BILITI)$', word)
        #print parse_stem
        if len(parse_stem) == 0:
            return word
        else:
            stem = self.to_consonant_vowel(parse_stem[0][0])
            m = (stem.values()[0]).count('VC')
            if m > 0:
                count = True
            else:
                return word

        if count == True:
            if (parse_stem[0][1] == 'ATIONAL' or parse_stem[0][1] == 'ATOR' or
                parse_stem[0][1] == 'ATION'):
                return stem.keys()[0] + 'ATE'
            elif (parse_stem[0][1] == 'TIONAL'):
                return stem.keys()[0] + 'TION'
            elif (parse_stem[0][1] == 'ENCI'):
                return stem.keys()[0] + 'ENCE'
            elif (parse_stem[0][1] == 'ANCI'):
                return stem.keys()[0] + 'ANCE'
            elif (parse_stem[0][1] == 'IZER' or parse_stem[0][1] == 'IZATION'):
                return stem.keys()[0] + 'IZE'
            elif (parse_stem[0][1] == 'ABLI'):
                return stem.keys()[0] + 'ABLE'
            elif (parse_stem[0][1] == 'ALLI' or parse_stem[0][1] == 'ALISM' or
                parse_stem[0][1] == 'ALITI'):
                return stem.keys()[0] + 'AL'
            elif (parse_stem[0][1] == 'ENTLI'):
                return stem.keys()[0] + 'ENT'
            elif (parse_stem[0][1] == 'ELI'):
                return stem.keys()[0] + 'E'
            elif (parse_stem[0][1] == 'OUSLI' or parse_stem[0][1] == 'OUSNESS'):
                return stem.keys()[0] + 'OUS'
            elif (parse_stem[0][1] == 'IVENESS' or parse_stem[0][1] == 'IVITI'):
                return stem.keys()[0] + 'IVE'
            elif (parse_stem[0][1] == 'FULNESS'):
                return stem.keys()[0] + 'FUL'
            elif (parse_stem[0][1] == 'BILITI'):
                return stem.keys()[0] + 'BLE'
            else:
                return word

    def step_3(self, word):
        '''
            Rules:
                (m>0) ICATE ->  IC
                (m>0) ATIVE ->
                (m>0) ALIZE ->  AL
                (m>0) ICITI ->  IC
                (m>0) ICAL  ->  IC
                (m>0) FUL   ->
                (m>0) NESS  ->
        '''
        parse_stem = re.findall(r'^(.*?)(ICATE|ATIVE|ALIZE|ICITI|ICAL|FUL|NESS)$', word)

        if len(parse_stem) == 0:
            return word

        #print parse_stem
        stem_consoant = self.to_consonant_vowel(parse_stem[0][0])
        m = (stem_consoant.values()[0]).count('VC')

        if m <= 0:
            return word

        if (parse_stem[0][1] == 'ICATE' or parse_stem[0][1] == 'ICITI' or
            parse_stem[0][1] == 'ICAL'):
            return parse_stem[0][0] + 'IC'
        elif (parse_stem[0][1] == 'ATIVE' or parse_stem[0][1] == 'FUL' or
            parse_stem[0][1] == 'NESS'):
            return parse_stem[0][0]
        elif (parse_stem[0][1] == 'ALIZE'):
            return parse_stem[0][0] + 'AL'
        else:
            return word
    def step_4(self, word):
        '''
            Rules:
                (m > 1) AL      ->
                (m > 1) ANCE    ->
                (m > 1) ENCE    ->
                (m > 1) ER      ->
                (m > 1) IC      ->
                (m > 1) ABLE    ->
                (m > 1) IBLE    ->
                (m > 1) ANT     ->
                (m > 1) EMENT   ->
                (m > 1) MENT    ->
                (m > 1) ENT     ->
                (m > 1 and (*S or *T)) ION ->
                (m > 1) OU      ->
                (m > 1) ISM     ->
                (m > 1) ATE     ->
                (m > 1) ITI     ->
                (m > 1) OUS     ->
                (m > 1) IVE     ->
                (m > 1) IZE     ->
        '''
        parse_stem = re.findall(r'^(.*?)(AL|ANCE|ENCE|ER|IC|ABLE|IBLE|ANT|EMENT|MENT|ENT|OU|ISM|ATE|ITI|OUS|IVE|IZE|ION)$', word)

        #print parse_stem
        if len(parse_stem) == 0:
            return word

        if parse_stem[0][1] != 'ION':
            consonant = self.to_consonant_vowel(parse_stem[0][0])
            m = (consonant.values()[0]).count('VC')
            if m > 0:
                return consonant.keys()[0]
            else:
                return word
        else:
            consonant = self.to_consonant_vowel(parse_stem[0][0])
            m = (consonant.values()[0]).count('VC')
            if m > 0:
                end_letter = re.findall(r'^(.*?)(S|T)$', consonant.keys()[0])
                if len(end_letter) != 0:
                    return consonant.keys()[0]
                else:
                    return word
            else:
                return word
    def step_5a(self, word):
        '''
            rules:
                (m > 1) E   ->
                (m = 1 and not *o) E ->
        '''
        parse_stem = re.findall(r'^(.*?)(E)$', word)
        if len(parse_stem) == 0:
            return word

        stem_consonant = self.to_consonant_vowel(parse_stem[0][0])
        m = (stem_consonant.values()[0]).count('VC')

        if m > 1:
            return stem_consonant.keys()[0]
        elif m == 1:
            stem_consonant = self.to_consonant_vowel(parse_stem[0][0], True)
            end_in_cvc = re.findall(r'^(.*?)(CVC)$', stem_consonant.values()[0])
            if len(end_in_cvc) == 0:
                return stem_consonant.keys()[0]
            else:
                second_c = (stem_consonant.keys()[0])[-1]
                if second_c == 'W' or second_c == 'X' or second_c == 'Y':
                    return stem_consonant.keys()[0]
                else:
                    return word
        else:
            return word

    def step_5b(self, word):
        '''
            Rule
            (m > 1 and *d and *L) -> single letter
        '''
        parse_stem = re.findall(r'^(.*?)(LL)$', word)

        if len(parse_stem) == 0:
            return word

        return parse_stem[0][0]+'L'

    def to_consonant_vowel(self, word, cvc_rule = False):
        '''
            This function converts the word into
            consonant and vowel ; which is C, V respectively.

            returns the dictionary { word: consonant_vowel}

            consonant:
                1) other than A,E,I,O,U
                2) other than y preceded by consonant
            Not consonant means = vowel

        '''
        letter_list = list(word)
        ret_list = []

        for letter in letter_list:
            if (letter == 'A' or letter == 'E' or letter == 'I' or letter == 'O' or letter == 'U'):
                ret_list.append('V')
            elif (letter == 'Y'):
                if (ret_list[len(ret_list)-1] == 'C'):
                    ret_list.append('V')
                else:
                    ret_list.append('C')
            else:
                ret_list.append('C')

        norm_dict = {}

        # if cvc_rule is True, then do not normalize the list
        if (cvc_rule == True):
            consonant_str = ''.join(ret_list)
            norm_dict[word] = consonant_str
        else:
            norm_list = self.normalize_list(ret_list)
            norm_list_str = ''.join(norm_list)
            norm_dict[word] = norm_list_str

        return norm_dict

    def normalize_list(self, consonant_vowel_list):
        #print consonant_vowel_list

        '''
            Have to reduce the list
            cccc... length > 0 is C
            vvvv... length > 0 is V
        '''

        ret_list = []
        prev_letter = ''

        if ( len(consonant_vowel_list) == 1):
            return consonant_vowel_list

        for letter in consonant_vowel_list:
            if (letter is not prev_letter):
                ret_list.append(letter)
                prev_letter = letter
            else:
                continue

        return ret_list

    def do_stem(self, word):
        step_1a = self.step_1a(word)
        step_1b = self.step_1b(step_1a)
        step_1c = self.step_1c(step_1b)
        step_2 = self.step_2(step_1c)
        step_3 = self.step_3(step_2)
        step_4 = self.step_4(step_3)
        step_5a = self.step_5a(step_4)
        stem = self.step_5b(step_5a)
        return stem

if __name__ == "__main__":
    user_input = raw_input()
    sw = StemWord()

    step_1a = sw.step_1a(str(user_input))
    #print stem_1a

    step_1b = sw.step_1b(step_1a)
    #print stem_1b

    step_1c = sw.step_1c(step_1b)
    #print stem_1c

    step_2 = sw.step_2(step_1c)
    # print step_2

    step_3 = sw.step_3(step_2)
    # print step_3

    step_4 = sw.step_4(step_3)
    # print step_4

    step_5a = sw.step_5a(step_4)
    # print step_5a

    stem = sw.step_5b(step_5a)
    print stem
