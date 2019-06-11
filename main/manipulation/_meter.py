#===============================================================================
# METER
# Tools for evaluating the foot and stress distribution across words.
#
# EXPORTS
# get_symbolic_string, get_foot_match, get_all_metersets, filter_poems
# US, SS, EI
#===============================================================================

import main.options as o
from main.language._pronunciation import Syllable
import re, itertools

#===============================================================================
# METER
#===============================================================================

MIN_BEAT_PER_LINE = 2
MAX_BEAT_PER_LINE = 6
FACTORS = range(MIN_BEAT_PER_LINE, MAX_BEAT_PER_LINE + 1)

# Symbols for stress levels
EI = 'x'
US = 'a'
SS = US.upper()

# Acceptable feet (of course much fewer than all there could be)
FEET = (
        US + SS, # iamb
        SS + US, # trochee
        
        SS + US + US, # dactyl
        US + SS + US, # amphibrach
        US + US + SS, # anapest
        )

# Currently unused; point is to score a poem for adherence to metric scheme
SCHEMES = (
           (US + SS, 4), (US + SS, 5), (US + SS, 6), # iambic tetr, pent, hex
           (SS + US, 4), (SS + US, 5), (SS + US, 6), # trochaic tetr, pent, hex
           (SS + US + US, 4), # dactylic tetr
           (US + SS + US, 4), # amphibrachic tetr
           (US + US + SS, 4), # anapestic tetr
           )    

# Words where the pronunciation dictionary's stress is less than ideal
# for their likely stress role at the sentence level
UNSTRESSED = ('be being am is are was were been do does did have has had all'
              ' some we from at of as and or but not if nor than with'
              ' by up for out off in on to through')

EITHER = ('where when why what how whom each both most few you these those'
          ' this that i he she it they me him them there just my your our his'
          ' her their its')


def _get_either_permutations(foot: str) -> list:
    """Return the permutations of the given foot with EI for each character."""
    
    # Permutations overgenerated; take only those still close to original foot
    def _filter_perm(perm: str) -> bool:
        return all(perm[i] in (foot[i], EI) for i in range(len(foot)))
    
    # Get and filter permutations
    perms = itertools.permutations(foot + (EI * len(foot)))
    perms = set(''.join(perm[:len(foot)]) for perm in perms)
    perms = filter(_filter_perm, perms)
    
    return list(perms)
    

def _get_foot_pattern(foot: str) -> str:
    """
    Return a regex pattern for matching this foot. Certain leniencies are taken
    due to the difficulty of predicting natural stress at the sentence level.
    """
    
    variants = []
    
    # Base foot
    variants.append(foot)
    
    # Spondee / molossus
    variants.append(SS * len(foot))
    
    # Account for "either"
    variants.extend(_get_either_permutations(foot))
    
    # Join in regex "or" format
    return '|'.join(variants)


def _symbolize_syllable(syll: Syllable) -> str:
    """Return a symbol for the given stressed or unstressed syllable."""
    
    return SS if syll._is_stress() else US
    

def get_symbolic_string(words: list) -> str:
    """Return a footstring of words: each syllable converted to a symbol."""
    
    poem = ''
    for word in words:
        
        # Escape words whose natural stress in a sentence must be overridden
        if word.lower() in UNSTRESSED:
            poem += US
        elif word.lower() in EITHER:
            poem += EI
        else:
            poem += ''.join(_symbolize_syllable(syll) for syll in word.pron)
    
    return poem


#===============================================================================
# METERSETS
#===============================================================================

def get_foot_match(s: str, foot: str, lenient: bool=False) -> bool:
    """
    Return True if the given string consists only of the given foot,
    or with a couple of unused syllables after if the lenient flag is set.
    """
    
    # Formulate the regex pattern
    lenient_pattern = '([{}{}{}]{}1,{}{})?'.format(US, SS, EI,
                                                   '{', len(foot) - 1, '}')
    
    pattern = '^({})+'.format(_get_foot_pattern(foot))
    pattern += lenient_pattern + '$' if lenient else '$'
    
    # Flatten stress if the user has requested it
    if o.OPTIONS['FLATTEN_STRESS_M']:
        return re.match(pattern, s, re.IGNORECASE)          
    else:
        return re.match(pattern, s)


def _get_meterset(poem: str, foot: str) -> tuple:
    """Return a (foot, n_matches) tuple for the given foot and poem."""
    
    if get_foot_match(poem, foot, lenient=True):
        return foot, int(len(poem) / len(foot))
    

def _get_rhythmset(poem: str) -> tuple:
    """Return a (foot, n_matches) tuple for individual syllables."""
    
    if o.OPTIONS['FLATTEN_STRESS_M']:
        return US, len(poem)
    
    else:
        return SS, poem.count(SS)


def _get_line_lengths(meterset: tuple) -> list:
    """
    Return a list of (foot, n_feet_per_line) tuples for the given meterset
    tuple of the form (foot, n_matches).
    """
      
    new_metersets = []    
    foot, _ = meterset    
    
    for factor in FACTORS:
        
        # Should be twice as many per line if what we're counting is syllables
        factor *= 2 if foot is US else 1
        
        new_metersets.append((foot, factor))
        
    return new_metersets
    

def get_all_metersets(words: list) -> set:
    """Return a set of metersets and rhythmsets, depending on user options."""
    
    # Symbolize the poem into its stressed and unstressed syllables
    poem = get_symbolic_string(words)
    
    # Get and expand all metersets
    metersets = set()
    for foot in FEET:
        meterset = _get_meterset(poem, foot)
        metersets |= set(_get_line_lengths(meterset)) if meterset else set()
    
    # Get and expand rhythmset
    if o.OPTIONS['RHYTHM']:
        metersets |= set(_get_line_lengths(_get_rhythmset(poem)))
    
    return metersets

#===============================================================================
# POEM FILTERING : Currently a stub
#===============================================================================

def filter_poems(poems: list) -> list:
    """
    Reduce poems to those that match metrical schemes, and that are without
    orphans, according to the user's options.
    """
    
    #TODO
    return poems
