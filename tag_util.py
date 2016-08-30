from nltk.tag import brill, brill_trainer
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.tbl.template import Template  # <- ??
from nltk.tag.brill import Pos, Word

def word_tag_model(words, tagged_words, limit=200):
	fd = FreqDist(words)
	cdf = ConditionalFreqDist(tagged_words)
	most_freq = (word for word, count in fd.most_common(limit))

	return dict((word, cfd[word].max()) for word in most_freq)

def backoff_tagger(train_sents, tagger_classes, backoff=None):
	'''
		backoff tagger is needed when the program face with the 
		oov (out of vocabulary) words. So instead of tag them as 
		None, backoff tagger can help reduce problem.

		We will use some Regexp pattern for the back off
	'''
	for cls in tagger_classes:
		print 'Training ',
		print cls,
		print ' tagger on conll2000 corpus with backoff ',
		print backoff

		backoff = cls(train_sents, backoff=backoff)

	return backoff

def train_brill_tagger(initial_tagger, train_sents, **kwargs):
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

	# Template generates rule for the Brill Rules that Brill tagger gonna use it
	 
	templates = [
	       brill.Template(brill.Pos([-1])),  # rule can be generated using the previous POS tag
	       brill.Template(brill.Pos([1])),  # look at the next POS tag to generate a rule
	       brill.Template(brill.Pos([-2])),  # rule can be generated using the two previous POS tag
	       brill.Template(brill.Pos([2])),  # rule can be generated using the next two POS tag
	       brill.Template(brill.Pos([-2, -1])),  # look at the combination of the previous two words to learn transformation rule
	       brill.Template(brill.Pos([1, 2])),
	       brill.Template(brill.Pos([-3, -2, -1])),
	       brill.Template(brill.Pos([1, 2, 3])),
	       brill.Template(brill.Pos([-1]), brill.Pos([1])),
	       brill.Template(brill.Word([-1])),
	       brill.Template(brill.Word([1])),
	       brill.Template(brill.Word([-2])),
		   brill.Template(brill.Word([2])),
		   brill.Template(brill.Word([-2, -1])),
		   brill.Template(brill.Word([1, 2])),
		   brill.Template(brill.Word([-3, -2, -1])),
		   brill.Template(brill.Word([1, 2, 3])),
		   brill.Template(brill.Word([-1]), brill.Word([1])),
		]

	'''
		BrillTaggerTrainer(1st, 2nd, 3rd, ...)
			1st param initial_tagger: (Tagger) the baseline tagger
			2nd param templates : (list of templates) templates to be used in training
			3rd param trace: (int) verbosity level == information level u want to see
			4th param deterministic: (bool) if True, adjudicate ties deterministically
			5th ruleformat: (str) format of reported rules
	'''
	
	trainer = brill_trainer.BrillTaggerTrainer(initial_tagger, templates, deterministic=True, trace=True)
	return trainer.train(train_sents, max_rules=100, min_score=2)

