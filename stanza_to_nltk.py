# Converts a texed processed by stanza into an NLTK corpus

import nltk as nltk
from nltk.corpus.reader import conll
import stanza as stanza

from stanza.utils.conll import CoNLL

# stanza spanish tagging
nlp = stanza.Pipeline(lang='es')

# The input to this is arbitrary, it could be a file if you wanted.
doc = nlp("Yo soy Diego. Soy de Puerto Rico.")

# Convert to conll format
stanza_conll = CoNLL.convert_dict(doc.to_dict())

# Write to conll format file - we could write multiple files for multiple
# different input sources here
with open('conll.txt','w+') as f:
    f.write(CoNLL.conll_as_string(stanza_conll))

# The columns we want (maybe we can get more info, I'm not sure)
COLUMN_TYPES = ('ignore',
                'words',
                'ignore',
                'pos',
                'ignore',
                'ignore',
                'ignore',
                'ignore',
                'ignore',
                'ignore',)


# Turn the file into an NLTK corpus, you could have many files as a 'corpus'
conll_corpus = conll.ConllCorpusReader("./",["conll.txt"],COLUMN_TYPES)

