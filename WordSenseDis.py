
from nltk.corpus import wordnet as wn
from nltk.tokenize import sent_tokenize, word_tokenize
from PorterStem import StemWord as sw
from nltk.data import load
import re
import pickle

class WSD:
	'''
		Modified Lesk Algorithm

		ref:
			1) Adapted Lesk Algorithm for WSD by S. Banerjee
			www.d.umn.edu/~tpederse/Pubs/banerjee.pdf

			2)

		Desc:
			
			Step
				1) Sentence tokenize
				2) word tokenize
				3) word tagger using Brill's tagger trained on Brown Corpus
				4) Stem word
				

			TW = target word

			Setting up a context window
			1) Set a context window around a target word
				a. window size of 2 * n + 1 around the target,
			    n words to its left and right. I will choose
			    the window size as 3. so n = 1.

			    We could have chosed larger context window, but
			    it's going to be computationally intense.

			    We don't select the word if it belong to
			    {I, a, an, as, at, by, he, his, me, or, thou, us, who}

			2) Pass every word in this context window into
			the program.

			3) Words that do not occur in the WordNet will
			be ignored..

			4) If not enough word exist to TW's right and left,
			then add words from the other direction.

			Comparing the senses of words

			1) We need to compute a score for every combination of sense of words
			in the context window.

				a = 1st word
				b = 2nd word
				c = 3rd word

				a_1 = 1st word's 1st sense
				a_2 = 1st word's 2nd sense

				b_1, b_2 = 2nd word's 1st and 2nd sense
				c_1, c_2 = 3rd word's 1st and 2nd sense

				total of 8 combinations
				2 x 2 x 2 = 8

				possible combination
					1) a_1 - b_1 - c_1    T T T
					2) a_1 - b_1 - c_2    T T F
					3) a_1 - b_2 - c_1    T F T
					4) a_1 - b_2 - c_2    T F F
					5) a_2 - b_2 - c_2    F F F
					6) a_2 - b_2 - c_1    F F T
					7) a_2 - b_1 - c_2    F T F
					8) a_2 - b_1 - c_1    F T T

			Word's hyponyms and hypernyms, put them into a concatanated
			string.

			ex. synset('conviction.n.02').hyponyms()
			-> {murder convition}, {robbery conviction}, {rape conviction}
			then put their definition into one string
			concat_str = "conviction for murder; conviction for robbery; conviction for rape"

			2) Compare the gloss of each sense of the target word with
			concatenated glosses of all other words in the context window.

			Scoring mechanism
			1) number of words found to be common between two strings is the
			score of the sense of the TW, but use a square method
			if 2 tokens matched then 2^2 = 4 scores
			if 3 tokens matched then 3^3 = 9 scores
			And these words in these tokens have to be in consecutive order.
			If it is separated to each other, then it starts from 1 token, which is 1 score.

			2) The sense with the highest score is the most appropriate sense
			for that TW.



	'''
	def __init__(self):
		self.document = []
		self.sentence = []
		self.query = []
		self.stop_word = ['I', 'a', 'an', 'as', 'at', 'by',
		 				'he', 'his', 'me', 'or', 'thou',
		 				'us', 'who', 'of', 'and', 'the', 'she', 
		 				'this', 'that', 'these', 'those', 'is']
		self.symbols = ['>','<','.',',','!','?','-','\'']
		f = open('brill_tagger.pickle', 'rb')
		self.brill_tagger = pickle.load(f)
		f.close()

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

		word_token_list = [word_tokenize(sen) for sen in sen_list]

		for sent in word_token_list:
			for word in sent:

				if (word in self.stop_word):
					sent.remove(word)

				if (word in self.symbols):
					sent.remove(word)

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


					upper_case = sw().do_stem(word[0].upper())

					if (upper_case_check == True):
						lower_case = upper_case[0] + upper_case[1:].lower()
					else:
						lower_case = upper_case.lower()
							
					param = ( lower_case, word[1])
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

	def get_context_window(self, sent_list, window_size=3):
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
		for sent_list in sent_list:

			for word in sent_list:

				context.append(word)
				
				if (len(context) is window_size):
					ret_context.append(context)
					context = []

			if (len(context) is not 0):
				if (len(sent_list) >= 3):
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

	#TODO
	def get_sense(self, context_window):
		'''
			Param:

		'''
		return None

	#TODO
	def score_sense(self, sense):
		'''
			1) use square score method
		'''
		return None

	#TODO
	def hypo_concat(self, word):
		'''
			return a string that is concatenation of
			gloss of hyponyms
		'''
		return None

	#TODO
	def hype_concat(self, word):
		'''
			returna string that is concatenation of
			gloss of hypernym
		'''
		return None

	#TODO
	def sense_combination(self, senses):
		'''
			return a list of possible sense combination
		'''
		return None




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

	# get a Target word and non-target word in the context window size of 3
	context_window = wsd.get_context_window(stemmed_list)
	print 'Context window'
	print context_window

