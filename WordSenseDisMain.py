from WordSenseDis import *

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

	# -------------------------- upto here seems fine ---------------
	sys.exit()
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
