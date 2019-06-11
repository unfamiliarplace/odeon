#===============================================================================
# CORPORA
# Functions for loading prose and poetry corpora.
#
# EXPORTS
# load_poetry_corpus, load_prose_corpus
#===============================================================================

import options as o
from nltk.corpus.reader.plaintext import PlaintextCorpusReader


def _load_corpus(corpus_dir: str) -> PlaintextCorpusReader:
    """Return a corpus reader from the given directory."""
    
    return PlaintextCorpusReader(corpus_dir, '.*')


def load_poetry_corpus(corpus_name: str) -> PlaintextCorpusReader:
    """Return a corpus reader from the given directory of a poetry genre."""
    
    return _load_corpus(o.POEMS_BASE + corpus_name)


def load_prose_corpus(corpus_name: str) -> PlaintextCorpusReader:
    """Return a corpus reader from the given directory of a prose genre."""
    
    return _load_corpus(o.PROSE_BASE + corpus_name)
