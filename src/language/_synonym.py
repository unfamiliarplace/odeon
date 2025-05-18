#===============================================================================
# SYNONYM
# Functions for getting synonyms of words and measuring poeticness.
# 
# EXPORTS
# get_all_variants, get_rarest_variant, get_poeticest_variant
# get_rarity, get_poeticness
#===============================================================================

import options as o
import itertools

def _get_synonym_possibilities(words: list) -> list:
    """
    Return a parallel list to Words where each word is replaced by a set of
    its possible synonyms (including itself).
    """
    
    poss = []
        
    for word in words:
        poetic = word.get_poetic_synonyms()
        #rare = word.get_rare_synonyms()
        rare = set()
        
        both = poetic | rare
        both = sorted(both, key=lambda w: (w.poeticness, w.rarity))
        both = set(both[:o.OPTIONS['SYN_MAX']])
        
        both = both | {word}
        poss.append(both)
        
    return poss


def get_all_variants(words: list) -> list:
    """
    Return an exhaustive list of variants of the given Words. A variant is a
    list where each word is either itself or replaced by a 
    """
    
    poss = _get_synonym_possibilities(words)
    return itertools.product(*poss)


def _get_best_variant(words: list, cmp) -> list:
    """
    Return the best variant of the given Words, as determined by the given
    function for identifying the factor to compare on. A variant is a list
    where each word is either itself or replaced by a     
    """
    
    variant = []
    poss = _get_synonym_possibilities(words)
    for syns in poss:
        best = max(syns, key=cmp)
        variant.append(best)
    return variant


def get_rarest_variant(words: list) -> list:
    """
    Return the best variant of the given Words by finding the rarest
    synonym for each. (A Word may be its own rarest )
    """
    
    return _get_best_variant(words, lambda syn: syn.rarity)


def get_poeticest_variant(words: list) -> list:
    """
    Return the best variant of the given Words by finding the poeticest
    synonym for each. (A Word may be its own most poetic )
    """
    
    return _get_best_variant(words, lambda syn: syn.poeticness)

#===============================================================================
# INDIVIDUAL WORD POETICNESS & SYNOYNMS
#===============================================================================

def _get_poetry_score(s: str) -> float:
    """Return the frequency of s in the poetry corpus."""    
    
    return o.FD_POEMS[s] / o.FD_POEMS.N()


def _get_prose_score(s: str) -> float:
    """Return the frequency of s in the prose corpus."""
           
    return o.FD_PROSE[s] / o.FD_PROSE.N()


def get_poeticness(s: str) -> float:
    """Return the poeticness of s: poetry score less prose score."""    
        
    return 1 + _get_poetry_score(s) - _get_prose_score(s)


def get_rarity(s: str) -> float:
    """Return the rarity of s across both corpora."""
        
    freq = (1 / (1 + (o.FD_POEMS[s] + o.FD_PROSE[s]))
                / (o.FD_POEMS.N() + o.FD_PROSE.N()))
                
    return freq if freq else 0.0
