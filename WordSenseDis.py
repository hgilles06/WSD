#Load the wordnet corpus
from nltk.corpus import wordnet as wn

class WSD:
	'''
		Modified Lesk Algorithm
		
		ref: 
			1) Adapted Lesk Algorithm for WSD by S. Banerjee
			www.d.umn.edu/~tpederse/Pubs/banerjee.pdf

			2) 
		
		Desc:

			TW = target word
			1) Set a context window around a target word
				a. window size of 2 * n + 1 around the target, 
			    n words to its left and right. I will choose
			    the window size as 11. so n = 5
			
			2) Pass every word in this context window into
			the program.
			
			3) Words that do not occur in the WordNet will 
			be ignored..
			
			4) If not enough word exist to TW's right and left, 
			then add words from the other direction.

			5) Compare the gloss of each sesnse of the target word with
			concatenated glosses of all other words in the context window.

			6) number of words found to be common between two strings is the
			score of the sense of the TW.

			7) The sense with the highest score is the most appropriate sense
			for that TW.
			 


	'''
	def __init__(self):

if "__name__" == "__main__":
	wsd = WSD()