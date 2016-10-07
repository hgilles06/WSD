
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
			print "\n ** First Item **\n"
			print first_item
			print ''
			print "\n ** Target Item **\n"
			print target_item
			print ''
			print "\n ** Last Item **\n"
			print last_item
			print ''
		elif (len(sense_combo) is 2):
			print 'sense_combo has 2 items\n'
			first_item = sense_combo[0]
			target_item = sense_combo[1]
			print "\n ** First Item **\n"
			print first_item
			print ''
			print "\n ** Target Item **\n"
			print target_item
			print ''
		elif (len(sense_combo) is 1):
			print 'sense_combo has 1 item\n'
			return 0

		# compare first and the target word first
		print "Comparing the first and target.."
		lst_first_target_item = []
		lst_first_target_item.append(first_item)
		lst_first_target_item.append(target_item)

		# compare the target and the last item
		print "Comparing the target and the last"
		lst_target_last_item = []
		lst_target_last_item.append(target_item)
		lst_target_last_item.append(last_item)

		# compare the left NT and right NT
		print "Comparing the first and last"
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
		print "\n---- Compute_overlap() finished ----\n"
		return total_score