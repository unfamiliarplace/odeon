#===============================================================================
# SYNONYM DICTIONARY
# Functions to load a thesaurus locally or from the NLTK.
# 
# EXPORTS
# load_synd
#===============================================================================

import options as o

# Conditionally load all wordnet and pos tagging
WN, POS_TAG, WN_CONSTANTS = None, None, None

#===============================================================================
# FROM NLTK: Wrapper for dict, referencing NLTK Wordnet interface
#===============================================================================

def _penn_to_wn(penn: str):
    """Given a Penn-style POS tag, return the WN constant for that category."""
      
    PREFIX_TO_WN = {
             'N': WN_CONSTANTS.NOUN,
             'V': WN_CONSTANTS.VERB,
             'R': WN_CONSTANTS.ADV,
             'J': WN_CONSTANTS.ADJ
             }
    
    for penn_prefix, wn in PREFIX_TO_WN.items():
        if penn.startswith(penn_prefix):
            return wn
        
    else:
        return WN_CONSTANTS.NOUN


class NLTK_Syndict(dict):
    """Extends dict to override getting with a pull from nlk.corpus.wordnet."""
    
    # The tags we can synonymize. Others lead to mismatched inflections.
    OKAY_TAGS = {'JJ', 'MD', 'NN', 'RB', 'VB'}
        
    def __getitem__(self, word: str) -> set:
        """
        Return the list of synonyms for the given word.
        If it is not yet registered in this syndict, load and register it first.
        """
        
        return super().setdefault(word, self._load(word))
    
    def get(self, word: str, default=set()) -> set:
        """Alternate syntax for __getitem__ (which does not override get)."""
        
        syns = self[word]
        return syns if syns else default
    
    def _load(self, word: str) -> set:
        """
        Load the cleaned synonyms (synset lemmas) for the given word.
        Respect the synonym flexibility measure: how many synsets to look at.
        
        NAIVE ASSUMPTION: Synsets are sorted by relevance. (They are not...)
        """
        
        # Check that the tag indicates this is a word we can use
        penn_tag = POS_TAG([word])[0][1]
        if penn_tag not in self.OKAY_TAGS:
            return set()
        
        # Get synsets from wordnet
        else:        
            synsets = WN.synsets(word, _penn_to_wn(penn_tag))
            all_syns = (ss.lemma_names() for ss in synsets)
            
            # Ignore those with only one word (= same as the input word)
            all_syns = filter(lambda syns: len(syns) > 1, all_syns)
            all_syns = sorted(all_syns, key=type(self).cmp_syns, reverse=True)
            
            # Limit by flexibility
            flex = o.OPTIONS['SYN_FLEX']
            n = max(1, round(flex * len(all_syns) / 100))
            
            # Isolate and clean names
            all_syns = (syn for syns in all_syns[:n] for syn in syns)
            return set(syn for syn in all_syns if '_' not in syn)
    
    @staticmethod
    def cmp_syns(syns) -> tuple:
        """Return a tuple of values representing fitnesses of this synset."""
          
        # Underscores are bad since we can't use compound nouns
        underscores = 1 + (len([syn for syn in syns if '_' in syn]))
        
        return (1 / underscores,)


def _load_synd_from_nltk() -> dict:
    """Return a synonynm dictionary formed from the wn synsets in the NLTK."""
    
    # Load wordnet and pos tagging
    from nltk.corpus import wordnet
    from nltk import pos_tag
    from nltk.corpus.reader import wordnet as wordnet_constants
    
    # Set the constants to these
    global WN, POS_TAG, WN_CONSTANTS
    WN, POS_TAG, WN_CONSTANTS = wordnet, pos_tag, wordnet_constants

    return NLTK_Syndict()

#===============================================================================
# FROM FILE: Regular dictionary
#===============================================================================

def _load_synd_from_file(fname: str) -> dict:
    """Return a synonym dictionary read from the given filename."""
    
    synd = {}
    with open(fname, 'r', errors='ignore') as f:
        
        line = f.readline().strip()
        while line:
            
            # Remove quotation marks and brackets in the data.
            line = line.lower().replace('"', '')
            line = line.replace('[', '').replace(']', '')
            
            # Before the : is the key
            key, val = line.split(':')
            
            # Split, strip, and register synonyms
            syns = set()
            for syn in val.split(','):
                syn = syn.strip()
                if syn:
                    syns |= {syn}
            
            # Map
            # Frankly I don't trust that this thesaurus doesn't have duplicates
            existing = synd.setdefault(key, [])
            existing.extend(syns)

            line = f.readline().strip()
    
    return synd


def load_synd() -> dict:
    """Return a pronunciation dictionary, whether local or NLTK."""
    
    if o.OPTIONS['LOCAL_SYND']:
        return _load_synd_from_file(o.SYND_FNAME)
    else:
        return _load_synd_from_nltk()
