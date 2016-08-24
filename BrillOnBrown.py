'''
	I want to train a Brill's Tagger on CONLL2000
	
	Brill's tagger is a TBL (transformation based Learning) approach
	It is based on rules that specify what tag should be assigned
	to what words. It is a supervised technique; it assumes there is
	pre-tagged training corpus.

	Problem:
		It's not 100% accurate.
		It shows wrong result when input 
		ex: "I want to book a flight."

		The correct output for the word 'book' should be 'VB', but the program
		tags it as 'NN'.  

		Fortunately, it doesn't tag every word as NN when it's preceeded by 'To'. 
		ex: 'To read'
		output: (read: VB)
		which is correct output.

		So I need to research bit more for this.
'''

from nltk.tag import RegexpTagger, untag, UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger, AffixTagger, RegexpTagger
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.corpus import brown, treebank, conll2000
from tag_util import backoff_tagger, train_brill_tagger
import pickle

# train_sents = brown.tagged_sents(categories=['news'])[:40000]
# test_sents = brown.tagged_sents(categories=['news']) [40000:50000]
train_sents = conll2000.tagged_sents()
# some regex pattern that will be used for the RegexpTagger
regex_pattern = [
	    (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
	    (r'.*ould$', 'MD'),
	    (r'.*ing$', 'VBG'),
	    (r'.*ed$', 'VBD'),
	    (r'.*ness$', 'NN'),
	    (r'.*ment$', 'NN'),
	    (r'.*ful$', 'JJ'),
	    (r'.*ious$', 'JJ'),
	    (r'.*ble$', 'JJ'),
	    (r'.*ic$', 'JJ'),
	    (r'.*ive$', 'JJ'),
	    (r'.*ic$', 'JJ'),
	    (r'.*est$', 'JJ'),
	    (r'^a$', 'PREP')
	]


initial_tagger = backoff_tagger(train_sents, 
				[AffixTagger,UnigramTagger, BigramTagger, TrigramTagger], 
				backoff=RegexpTagger(regex_pattern))

# Training the Brill Tagger
brill_tagger = train_brill_tagger(initial_tagger, train_sents)
#print brill_tagger.evaluate(test_sents)

# Save pickle for the later use
f = open('brill_tagger.pickle','wb')
pickle.dump(brill_tagger, f)
f.close()