from nltk.tbl.template import template  # <- ??
from nltk.tag.brill import Pos, Word
from nltk.tag import RegexpTagger
from nltk.tag.brill_trainer_orig import BrillTaggerTrainer
from nltk.corpus import brown

training_data = brown.tagged_sents(categories=['news'])[:100]
baseline_data = brown.tagged_sents(categories=['news'])[100:200]
gold_data = brown.tagged_sents(categories=['news'])[200:300]