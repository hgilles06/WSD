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


def backoff_tagger(train_sents,tagger_classes, backoff=None):
   for cls in tagger_classes:
     backoff = cls(train_sents, backoff=backoff)
   return backoff


'''
from nltk.tbl.template import Template  # <- ??
from nltk.tag.brill import Pos, Word
from nltk.tag import RegexpTagger, untag, UnigramTagger, BigramTagger, TrigramTagger, DefaultTagger
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.corpus import brown, treebank
from tag_util import backoff_tagger, train_brill_tagger

train_sents = brown.tagged_sents(categories=['news'])[:3000]
test_sents = brown.tagged_sents(categories=['news']) [3000:]

# backoff = RegexpTagger([
# 		(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
# 		(r'(The|the|A|a|An|an)$','AT'),  # articles
# 		(r'.*ables$', 'JJ'),  # adjectives
# 		(r'.*ness$', 'NN'),  # nounds formed from adjectives
# 		(r'.*ly$', 'RB'),  # adverbs
# 		(r'.*s$','NNS'),  # plural nouns
# 		(r'.*ing$','VBG'),  # gerunds
# 		(r'.*ed$', 'VBD'),  # past tense verbs
# 		(r'.*', 'NN')	# nouns (default)
# 		])

# Tagging using without Brill tagger
default_tagger = DefaultTagger('NN')
initial_tagger = backoff_tagger(train_sents, [UnigramTagger, BigramTagger, TrigramTagger], backoff=default_tagger)
#print initial_tagger.evaluate(test_sents)

# Tagging using Brill tagger trained on Brown corpus
brill_tagger = train_brill_tagger(initial_tagger, train_sents)
#print brill_tagger.evaluate(test_sents)
print brill_tagger.tag(['She', 'wants','to','book','a','room'])
