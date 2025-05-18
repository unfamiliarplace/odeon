#===============================================================================
# PRONUNCIATION DICTIONARY
# Functions to load a map of words to phonemes locally or from the NLTK.
# 
# EXPORTS
# load_prond
#===============================================================================

import options as o

#===============================================================================
# FROM NLTK: CMU Dict
#===============================================================================

def _load_prond_from_nltk() -> dict:
    """Return the pronunciation dictionary included in the NLTK."""
    
    from nltk.corpus import cmudict
    prond = cmudict.dict() #@UndefinedVariable # LazyLoaded
    return {k: v[0] for k, v in prond.items()} # They are embedded in sublists

#===============================================================================
# FROM FILE: Regular dictionary, Canadianized & slightly customized
#===============================================================================

def _load_prond_from_file(fname: str) -> dict:
    """Return a pronunciation dictionary read from the given filename."""
    
    prond = {}
    with open(fname, 'r', errors='ignore') as f:
        
        line = f.readline().strip()
        while line:
            
            if line[0].isalpha():
                word, pron = line.split('  ')
                
                # Ignore secondary pronunciations
                # Lowercase all
                if not word.endswith(')'):
                    prond[word.lower()] = pron.split()

            line = f.readline().strip()
    
    return prond


def load_prond() -> dict:
    """Return a pronunciation dictionary, whether local or NLTK."""

    if o.OPTIONS['LOCAL_PROND']:
        return _load_prond_from_file(o.PROND_FNAME)
    else:
        return _load_prond_from_nltk()
