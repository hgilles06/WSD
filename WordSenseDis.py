
from nltk.tokenize import sent_tokenize, word_tokenize
from PorterStem import StemWord as sw
from nltk.data import load
from nltk.corpus import wordnet as wn
from collections import OrderedDict, defaultdict
import re
import pickle
import itertools
import sys
import nltk


class WSD:

	def __init__(self):
		self.document = []
		self.sentence = []
		self.query = []
		self.stop_word = ['I', 'a', 'an', 'as', 'at', 'by', 'the', 'in', 'of',
		 				  'his', 'me', 'or', 'for',
		 				  'us', 'who', 'and', 'the', 'She', 'He', 
		 				  'this', 'that', 'these', 'those', 'is', 'They', 'Their']
		
		self.symbols = ['>', '<', '.', ',', '!', '?', '-', '\'', '--', ')', '(', ';']
		
		# load up the brill tagger
		f = open('brill_tagger.pickle', 'rb')
		self.brill_tagger = pickle.load(f)
		f.close()

		self.synsets_pos_list = ['ADJ', 'ADJ_SAT', 'ADV', 'NOUN', 'VERB']
		self.vb_tag_list = ['VBZ', 'VB', 'VBD', 'VBG', 'VBN', 'VBP']
		self.noun_tag_list = ['NN', 'NNS', 'NNPS']
		self.adj_tag_list = ['JJ', 'JJR']
		self.adv_tag_list = ['RB']

	def get_document(self, docs):
		self.document = docs

	def get_sentence(self, sentence):
		self.sentence = sentence

	def get_query(self, query):
		self.query = query

	def tokenize_sen(self, docs):
		sentence_list = sent_tokenize(docs)
		return sentence_list

	def tokenize_word(self, sen_list):
		'''
			param:
				sen_list = [[sentence 1], [sentence 2]]
			return:
				[[words in sentence 1], [words in sentence 2]]
		'''

		word_token_list = [word_tokenize(sen) for sen in sen_list]

		return word_token_list

	def porter_stem(self, sen_list):
		'''
			Param:
				[ [("hello")], [('Hello2')] ]
			Return :
				[ [('She','PRP'), ('to','To')], [('He', 'PRP')] ]
		'''
		ret_list = []
		word_pos = []

		# because stem() returns every words in capital, so we want to store
		# a word in its original form
		upper_case_check = False

		for sent in sen_list:
			for word in sent:
				if (word[0] not in self.stop_word) and (word[0] not in self.symbols):

					if (word[0][0].isupper()):
						upper_case_check = True
					else:
						upper_case_check = False

					upper_case = sw().do_stem(word[0].upper(), word[1])

					if (upper_case_check is True):
						lower_case = upper_case[0] + upper_case[1:].lower()
					else:
						lower_case = upper_case.lower()
							
					param = (lower_case, word[1])
					word_pos.append(param)
				else:
					word_pos.append(word)
			
			ret_list.append(word_pos)
			
			word_pos = []  # reset the list, so we can avoid duplicate list

		return ret_list

	def word_tagger(self, word_list):
		'''
			Param:
				word_list: list of tokenized words
					ex: ['My','name','is','blah']
			Return:
				list of tokenized words with its POS
				ex :[('she', 'PPS'),('wants','VBZ')...]
		'''
		brill_tagger = self.brill_tagger
		return brill_tagger.tag(word_list)

	def remove_stop_word_with_tag(self, tagged_list):
		'''
			param:
				tagged_list : [ [('she', tag), ('is', tag), ('angry', tag)] ....]
			return:
				tagged_list : [[('angry', tag)]...]
		'''
		word_list = []
		sent_list = []

		for sent in tagged_list:
			for word in sent:
				if ((word[0] not in self.stop_word) and (word[0] not in self.symbols)):
					word_list.append(word)
			sent_list.append(word_list)
			word_list = []

		return sent_list

	def remove_symbols_and_stop(self, word_list):
		ret_list = []
		for word in word_list:
			if (word not in self.symbols) and (word not in self.stop_word):
				ret_list.append(word)

		return ret_list

	def get_context_window(self, sent_lists, window_size=3):
		'''
			Param:
				sent_list = [[('She','PRP'), ('is','DT'), ('the','DT') ],
								[('He','PRP'),('is','DT'), ('the','DT')] ]
				window_size = pick a number of context window size
			Ret:
				if window_size = 3
					[Non-target-word, Target-word, Non-target-word]
		'''
		context = []
		ret_context = []
		for sent_list in sent_lists:

			for word in sent_list:

				context.append(word)

				if (len(context) is window_size):
					ret_context.append(context)
					context = []

			# case when there is less than window size words in a sentence.
			if (len(ret_context) is 0):
				if(len(context) is not 0):
					ret_context.append(context)
					context = []

			# case when there isn't enough words for the next context window
			if (len(context) is not 0):
				if (len(sent_list) >= window_size):
					short_amount = window_size - len(context)
					short_amount = short_amount * (-1)
					previous_context = ret_context[-1]
					context_to_add = previous_context[short_amount:]

					context = context_to_add + context
					ret_context.append(context)
					context = []
				else:
					ret_context.append(context)

		return ret_context

	def get_senses(self, context):
		'''
			Param:
				context_window = [ [(non-target, its tag),(target, its tag),(non-target, its tag)] ... ]
			ret:
				OrderedDictionary = { ( (non-target) : [synsets1, synsets2, ...] ),
									  ( (target) : [synset1, synset2, ...] ),
									  ( (non-target): [synset1, synset2, ...] ),
									  ...
									  }
		'''
		tag = ''
		synset_list = []
		print "context ......",
		print context

		for word in context:

			if (str(word[1]) in self.vb_tag_list):
				senses = wn.synsets(word[0], pos=wn.VERB)
				tag = 'v'
			elif (str(word[1]) in self.noun_tag_list):
				senses = wn.synsets(word[0], pos=wn.NOUN)
				tag = 'n'
			elif (str(word[1]) in self.adj_tag_list):
				senses = wn.synsets(word[0], pos=wn.ADJ)
				tag = 'adj'
			elif (str(word[1]) in self.adv_tag_list):
				senses = wn.synsets(word[0], pos=wn.ADV)
				tag = 'adv'
			else:
				# TODO: handle case when the tag is None
				# might have to use nltk.pos_tag(word[0])
				senses = ''
				tag = ''

			print "senses: ",
			print senses

			synset_list.append(senses)

		return synset_list

	def sense_combination(self, synset_list):
		'''
			params:
				senses = [
					[Synset('angry.0.1'), Synset('angry.0.2')...],
					[Synset('mad.0.1'), Synset('mad.0.2')...]
				]
			Return:
				list = [[a1,a2], [b1, b2] ,[c1,c2]]

				cartesian combination = [ [a1,b1,c1] , [a1,b1,c2] , [a1,b2,c1] ..]
		'''
		combo_synset_list = []

		# * unpacks the item in the list
		combo_synset_list = list(itertools.product(*synset_list))

		return combo_synset_list

	def get_def_hypo_hype(self, synset_list, opt=''):
		'''
			Params:
				synset is something like 'sentence.n.02' =>
					* 'sentence' is a word
					* n means noun
					* 02 means it is a 2nd noun in the list.
			Return:
				return a string that is concatenation of
				gloss of hyponyms or hypernyms
		'''
		ret_list = []
		hypo = ''
		hype = ''
		for syn in synset_list:
			for item in syn.hyponyms():
				hypo = hypo + str(item.definition())
				hypo = hypo + '; '

			for item in syn.hypernyms():
				hype = hype + str(item.definition())
				hype = hype + '; '

			ret_list.append((str(syn.definition()), hypo, hype))

		print '\nDef_hypo_hype of the synsets for'
		print synset_list
		print ''
		print ret_list
		return ret_list

	def overlap_score(self, sense_combo, context=''):
		# check if the sense combo has 3 items or less in the list
		# first and last item are the non-target word in the context window
		last_item = []
		target_item = []
		first_item = []

		print "\n\n****** [Synset definition, Synset's hyponyms, Synset's Hypernyms] ****** \n\n"

		if(len(sense_combo) is 3):
			print 'sense_combo has 3 items\n'
			first_item = sense_combo[0]
			target_item = sense_combo[1]
			last_item = sense_combo[-1]
			print first_item
			print ''
			print target_item
			print ''
			print last_item
			print ''
		elif (len(sense_combo) is 2):
			print 'sense_combo has 2 items\n'
			first_item = sense_combo[0]
			target_item = sense_combo[1]
			print first_item
			print ''
			print target_item
			print ''
		elif (len(sense_combo) is 1):
			print 'sense_combo has 1 item\n'
			return 0

		# compare first and the target word first
		lst_first_target_item = []
		lst_first_target_item.append(first_item)
		lst_first_target_item.append(target_item)

		# compare the target and the last item
		lst_target_last_item = []
		lst_target_last_item.append(target_item)
		lst_target_last_item.append(last_item)

		# compare the left NT and right NT
		lst_first_last_item = []
		lst_first_last_item.append(first_item)
		lst_first_last_item.append(last_item)

		# cartesian product comparing
		compare_list_LT = []
		compare_list_LT = list(itertools.product(*lst_first_target_item))

		print '\nCombination of the def hype hypo combo: '
		for a in compare_list_LT:
			print a
			print ''
		sys.exit()
		sen1 = ''
		sen2 = ''
		sen3 = ''
		total_score = 0

		# comparing for the Left non target word and the target word
		if (len(sense_combo) > 1):
			for pair in compare_list_LT:
				sen1 = pair[0]
				sen2 = pair[1]
				total_score = total_score + self.compute_overlap(sen1, sen2)

		# comparing fot the target word and the right non-target word
		compare_list_TR = []

		if (len(sense_combo) > 2):
			compare_list_TR = list(itertools.product(*lst_target_last_item))
			for pair in compare_list_TR:
				sen2 = pair[0]
				sen3 = pair[1]
				total_score = total_score + self.compute_overlap(sen2, sen3)

		# comparing the first and the last non target
		compare_list_LR = []

		if (len(sense_combo) > 2):
			compare_list_LR = list(itertools.product(*lst_first_last_item))
			for pair in compare_list_LR:
				sen1 = pair[0]
				sen3 = pair[1]
				total_score = total_score + self.compute_overlap(sen1, sen3)

		return total_score

	# TODO
	def compute_overlap(self, sen1, sen2):

		print "\n---- Compute_overlap() is start ---\n"

		sen1_word_list = word_tokenize(sen1)
		sen2_word_list = word_tokenize(sen2)

		edit_sen1 = self.remove_symbols_and_stop(sen1_word_list)
		edit_sen2 = self.remove_symbols_and_stop(sen2_word_list)

		edit_sen1_str = ' '.join(edit_sen1)
		edit_sen2_str = ' '.join(edit_sen2)

		print 'sen a: ' + edit_sen1_str + '\n'
		print 'sen b: ' + edit_sen2_str + '\n'

		temp = ''
		overlap_lst = []
		overlap_removed_sen2 = ''
		for word in edit_sen1_str.split():
			temp = temp + word

			# print "checking for : " + temp + '\n'
			# must check if a word exist as a whole word, not as a substring of a word
			# in Regex, \b matches the emptry string at the beginning or end of a word
			search = re.search(r'\b%s\b' % temp, edit_sen2_str)
			if (search):
				# print "temp is in the second sentence " + temp + "\n"
				temp = temp + ' '
			else:

				temp = temp[:-len(word)]  # remove the current word from the string
				temp = temp.strip()  # remove leading and trailing spaces

				# replace the first item that overlap in the sentence
				overlap_removed_sen2 = edit_sen2_str.replace(temp, "", 1)
				edit_sen2_str = overlap_removed_sen2
				edit_sen2_str = edit_sen2_str.strip()

				if (len(temp) > 0):
					overlap_lst.append(temp)

				temp = ''

		# if temp is not empty, means there was a overlap at the end
		# else there was no overlap at the end
		if (len(temp) > 0):
			temp = temp.strip()
			#print temp
			if (edit_sen2_str.count(temp) > 0):
				overlap_lst.append(temp)

		if (len(overlap_lst) > 0):
			print overlap_lst
		else:
			print "Couldn't find overlap..\n"

		total_score = 0
		overlap = 0

		for sen in overlap_lst:
			for item in sen.split():
				# print item
				overlap = overlap + 1
			overlap = overlap ** 2
			total_score = total_score + overlap
			print "Score for '%s' is : %d" % (sen, overlap)
			overlap = 0

		print "Total score : %d" % (total_score)
		print "\n---- Computer_overlap() finished ----\n"
		return total_score


if __name__ == "__main__":
	wsd = WSD()
	user_input = raw_input()
	print '\n'

	# setence tokenize
	sen_list = wsd.tokenize_sen(user_input)
	print 'Sentence token: '
	print sen_list
	print '\n'

	# word tokenize
	word_list = wsd.tokenize_word(sen_list)
	print 'Word token: '
	print word_list
	print '\n'

	# tag each word in the sentence
	tagged_list = []
	for sent in word_list:
		tagged_list.append(wsd.word_tagger(sent))
	print 'Tagged word list'
	print tagged_list
	print '\n'

	# stem each word
	stemmed_list = wsd.porter_stem(tagged_list)
	print 'After porter stemmed'
	print stemmed_list
	print '\n'

	# remove the stopword and symbols from the list
	print 'Removed stop word from the list'
	removed_stop_list = wsd.remove_stop_word_with_tag(stemmed_list)
	print removed_stop_list
	print '\n'

	# get a Target word and non-target word in the context window size of 3
	context_window = wsd.get_context_window(removed_stop_list)
	print 'Context window'
	print context_window
	print '\n'

	# get the sense of each word in the context.
	senses_list = []
	synsets_combo_list = []
	# context is a sub_list
	# TODO: get score for each context in context_window
	# context is a three words that has to be disambiguated..
	for context in context_window:
		# get synset for each word in the context
		synsets_of_context = wsd.get_senses(context)
		print '\nContext:',
		print context
		print '\nSynsets of each word in context'
		print synsets_of_context
		print '\nlength of all synsets: %d' % (len(synsets_of_context))
		print '\nSynsets combination'
		# get all possible combination with found synsets
		synsets_combo_list = wsd.sense_combination(synsets_of_context)
		print synsets_combo_list
		print '\nTotal of combination: %d' % (len(synsets_combo_list))
		for synset_combo in synsets_combo_list:
			synset_combo_hypo_hype = wsd.get_def_hypo_hype(synset_combo)
			wsd.overlap_score(synset_combo_hypo_hype)



'''
	print "context_window: ",
	print context_window
	print '\nsense list: ',
	print senses_list
	sys.exit()

	# get a sense combination of each context window
	combo = []
	list_of_combo = []
	for sens in senses_list:
		print sens
		sys.exit()
		combo = wsd.sense_combination(sens, len(sens))
		print "Possible sense combination\n"
		for c in combo:
			print c
			print ''
		print 'total of %d combinations found\n' % (len(combo))
		list_of_combo.append(combo)

	print "length of list of combo: %d" % (len(list_of_combo))
	# print list_of_combo
	# sys.exit()
	# for each sense combination
	# we need to get the hype and hypo of each sense in combination
	gloss_hype_hypo = []
	gloss_hype_hypo_dict = {}
	gloss = ''
	hype = ''
	hypo = ''

	# list_of_combo = [ [combo 1], [combo 2], ... , [combo n]]
	# combo = combination of three words [ context1, context2, ... , context n]
	# combo1 : all combination of the synsets of the first three words
	# combo2 : all combination of the synsets of the next three words
	# context_i = [(synset 1 of left non target), (synset 1 of target), (synset 1 of right non target)]
	# TODO: make this into a function
	for combo in list_of_combo:
		for context in combo:
			for word in context:
				# print word
				gloss = str(word.definition())
				hypo = wsd.get_hypo_hype(word, 'hypo')
				hype = wsd.get_hypo_hype(word, 'hype')
				gloss_hype_hypo.append([gloss, hypo, hype])
			gloss_hype_hypo_dict[context] = gloss_hype_hypo
			gloss_hype_hypo = []

	print gloss_hype_hypo_dict
	print len(gloss_hype_hypo_dict)
	
	score = 0
	score_for_context = defaultdict(int)

	i = 0
	for key, value in gloss_hype_hypo_dict.iteritems():
		print "\n------ key is --------\n"
		print key
		print '\n'
		print value
		print ''
		score = wsd.overlap_score(value, key)
		print 'score is %d \n' % (score)
		score_for_context[key] = score
		score = 0

	for key, value in score_for_context.iteritems():
		print key, value
		print ''

	print "Total item in the list: %d" % (len(score_for_context))
	# print "\ntotal overlap score is %d " % (score)
	# need to compare two items at a time.
	# [[a's gloss, a's hypo , a's hype], [b's gloss, b's hypo, b's hype], [c's gloss, c's hypo, c's hype] ]
	#  we want to compare [0] & [1] then [1] & [2]
'''
	