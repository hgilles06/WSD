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
from nltk.tag import RegexpTagger, untag, UnigramTagger, BigramTagger, TrigramTagger
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.corpus import brown

training_data = brown.tagged_sents(categories=['news'])[:1000]
baseline_data = brown.tagged_sents(categories=['news'])[1000:2000]
gold_data = brown.tagged_sents(categories=['news'])[2000:3000]
testing_data = [untag(s) for s in gold_data]

'''
	backoff tagger is needed when the program face with the 
	oov (out of vocabulary) words. So instead of tag them as 
	None, backoff tagger can help reduce problem.

	We will use some Regexp pattern for the back off
'''

backoff = RegexpTagger([
		(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),  # cardinal numbers
		(r'(The|the|A|a|An|an)$','AT'),  # articles
		(r'.*ables$', 'JJ'),  # adjectives
		(r'.*ness$', 'NN'),  # nounds formed from adjectives
		(r'.*ly$', 'RB'),  # adverbs
		(r'.*s$','NNS'),  # plural nouns
		(r'.*ing$','VBG'),  # gerunds
		(r'.*ed$', 'VBD'),  # past tense verbs
		(r'.*', 'NN')	# nouns (default)
		])

baseline = backoff   # better baseline uses Unigram tagger (??)

'''
	some suggested rules for the template
		change the POS of a word, depending on the POS of the previous word
		change the POS of a word, depending on the POS of any of the two previous words
		change the POS of a word, depending on the POS of any of the three previous words
		change the POS of a word, depending on the POS of the previous word and the POS of the next word
		change the POS of a word, depending on the previous word
		change the POS of a word, depending on any of the two previous words
		change the POS of a word, depending on any of the three previous words
		change the POS of a word, depending on the previous word and the next word
'''

# construct template
Template._cleartemplates()  # clear any templates created in eariler tests

#templates = [Template(Pos([-1])), Template(Pos([-1]), Word([0]))]

templates = [
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
    brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
    brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1))
]

# construct a Brill Tagger Trainer
'''
	BrillTaggerTrainer(1st, 2nd, 3rd, ...)
		1st param initial_tagger: (Tagger) the baseline tagger
		2nd param templates : (list of templates) templates to be used in training
		3rd param trace: (int) verbosity level == information level u want to see
		4th param deterministic: (bool) if True, adjudicate ties deterministically
		5th ruleformat: (str) format of reported rules
'''
ret = BrillTaggerTrainer(baseline, templates, trace=3)

tagger1 = ret.train(training_data, max_rules=10)