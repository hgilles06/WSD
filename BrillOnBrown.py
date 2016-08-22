'''
	I want to train a Brill's Tagger on Brown Corpus
	
	Brill's tagger is a TBL (transformation based Learning) approach
	It is based on rules that specify what tag should be assigned
	to what words. It is a supervised technique; it assumes there is
	pre-tagged training corpus.
'''
'''
	how to save and load trained tagger
   
	import pickle

	# save
	f = open('tagger.pickle', 'wb')
	pickle.dump(tagger, f)
	f.close()

	#load
	f = open('tagger.pickle', 'rb')
	tagger = pickle.load(f)

'''

from nltk.tag import RegexpTagger, untag, UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.corpus import brown, treebank
from tag_util import backoff_tagger, train_brill_tagger
import pickle

train_sents = brown.tagged_sents(categories=['news'])[:10000]
test_sents = brown.tagged_sents(categories=['news']) [10000:20000]

# Tagging using without Brill tagger
default_tagger = DefaultTagger('NN')
initial_tagger = backoff_tagger(train_sents, [UnigramTagger, BigramTagger, TrigramTagger], backoff=default_tagger)
#print initial_tagger.evaluate(test_sents)

# Tagging using Brill tagger trained on Brown corpus
brill_tagger = train_brill_tagger(initial_tagger, train_sents)
#print brill_tagger.evaluate(test_sents)
#print brill_tagger.tag(['She', 'wants','to','race','a','room'])

# Save pickle for the later use
f = open('brill_tagger.pickle','wb')
pickle.dump(brill_tagger, f)
f.close()