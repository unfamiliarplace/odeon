#===============================================================================
# PRONUNCIATION
# Models a syllable and provides pronunciation tools.
# 
# EXPORTS
# Syllable, syllabify, get_pron, pron_sim, no_rhyme, no_syns
#===============================================================================

import options as o
from external import num2words
import re, itertools

#===============================================================================
# VOWEL & CONSONANT FEATURES
#===============================================================================

# Vowels are classified by closeness (1-7), backness (1-5), & rounded (0|1).
VOWELS = {
          # MONOPHTHONGS
          'AA': (1, 5, 0),
          'AE': (2, 2, 0), 
          'AH': (3, 3, 0),
          'AO': (1, 5, 1),
          'EH': (3, 2, 0),
          'ER': (4, 3, 0),
          'EY': (5, 1, 0),
          'IH': (6, 2, 0),
          'IY': (7, 1, 0),
          'OW': (5, 5, 1),
          'UH': (6, 4, 1),
          'UW': (7, 5, 1),
          
          # DIPHTHONG-ONLY: symbols not in CMU, invented for this purpose
          
          'AX': (1, 2, 0), # [a]
          'OH': (3, 5, 1), # open o
          'EE': (5, 1, 0), # [e]
          # 'UU': (7, 5, 1), # [u] # For a diphthong not being used
          # 'II': (7, 1, 0), # [i] # For a diphthong not being used
          }

# DIPHTHONGS (halfway between their two vowels)
DIPHTHONGS = {
              'AW': ('AX', 'UH'),
              'AY': ('AX', 'IH'),
              'OY': ('OX', 'IH'),
              'EY': ('EE', 'IH'),
              # 'IY': ('II', 'IH'), # Involves semivowel, unquantifiable now
              # 'UW': ('UU', 'UH'), # Involves semivowel, unquantifiable now
              }

# Consonants are classified by voiced (0|1), backness (1-13), & sonority (1-6).
CONSONANTS = {
              # STOPS              
              'P':  (0, 1,  1),
              'T':  (0, 4,  1),
              'K':  (0, 10, 1),
              'B':  (1, 1,  1),
              'D':  (1, 4,  1),
              'G':  (1, 10, 1),
              
              # AFFRICATES
              'CH': (0, 6,  2),
              'JH': (1, 6,  2),
              
              # FRICATIVES
              'F':  (0, 2,  3),
              'TH': (0, 4,  3),
              'S':  (0, 5,  3),
              'SH': (0, 6,  3),
              'V':  (1, 2,  3),
              'DH': (1, 4,  3),
              'Z':  (1, 5,  3),
              'ZH': (1, 6,  3),
              'HH': (0, 13, 3),
              
              # NASALS
              'M':  (1, 1,  4),
              'N':  (1, 5,  4),
              'NG': (1, 10, 4),
              
              # LIQUIDS: must be manually distinguished by laterality!
              'L':  (1, 5,  5),
              'R':  (1, 5,  5),
              
              # GLIDES
              'Y':  (1, 2,  5),
              'W':  (1, 12, 5)
              }

#===============================================================================
# CONSONANT CLUSTERS
#===============================================================================

# Initial clusters. Recursive, e.g. S -> T -> R
C_CLUSTERS_I = {
                'TH': tuple('R'),
                'T':  tuple('RW'),
                'D':  tuple('RW'),
                'P':  tuple('RL'),
                'K':  tuple('RLW'),
                'B':  tuple('RL'),
                'G':  tuple('RLW'), 
                'F':  tuple('RL'),
                'S':  tuple('WTPNMLK'),
              }

# Final clusters. Recursive, e.g. R -> V -> D
C_CLUSTERS_F = {           
                'P':  tuple('LMRS'),
                'T':  tuple('FKLMNPRS') + ('CH', 'SH', 'TH'),
                'K':  tuple('LRS') + ('NG',),
                'B':  tuple('LRM'),
                'D':  tuple('BGLNMRVZ') + ( 'JH', 'ZH', 'DH', 'NG'),
                'G':  tuple('LR'),
                'CH': tuple('LRNT'), # T ?
                'JH': tuple('LRN'),
                'F':  tuple('LRMNP'),
                'TH': tuple('LRNT'),
                'S':  tuple('FKNPRT') + ('TH',),
                'SH': tuple('LRN'),
                'V':  tuple('LR'),
                'DH': tuple('R'),
                'Z':  tuple('BDGLNRV') + ('DH','NG'),
                'ZH': tuple('D'), # ?
                'M':  tuple('LR'),
                'N':  tuple('LR'),
              }

#===============================================================================
# SYLLABLE
#===============================================================================

class Syllable:
    """Models a syllable with stress, onset,  nucleus, and coda."""    
    
    def __init__(self, stress: int, onset=[], nucleus=[], coda=[]):
        """Initialize this Syllable. If O, N, and C are supplied, save them."""
        
        self.stress = stress
        self.onset = tuple(onset)
        self.nucleus = tuple(nucleus)
        self.coda = tuple(coda)
        
    
    def __repr__(self) -> str:
        """Return a string representation of this Syllable."""
        
        return 'Syl({}): o{} | n{} | c{}'.format(self.stress, self.onset,
                                                 self.nucleus, self.coda)
        
        
    def __eq__(self, other) -> bool:
        """Return True iff this Syllable has the same parts as the other."""
        
        return repr(self) == repr(other)
        
    
    def __hash__(self) -> int:
        """Return the hash of this Syllable's string representation."""
        
        return hash(str(self))
    
    
    def __bool__(self) -> bool:
        """Return True iff this Syllable has a nucleus."""
        
        return bool(self.nucleus)
        
    
    def _is_stress(self) -> bool:
        """Return True iff this is a stressed syllable."""
        
        # 0 is unstressed, 1+ is stressed
        return bool(self.stress)


#===============================================================================
# SYLLABIFYING
#===============================================================================

def _get_nuclear_cluster(phon: str) -> tuple:
    """Return the nuclear cluster represented by the phoneme."""
    
    phon = phon[:-1]
    
    if phon in VOWELS:
        return phon,
    
    elif phon in DIPHTHONGS:
        return DIPHTHONGS[phon]


def syllabify(pron: list) -> list:
    """Return a list of the syllables from the given list of phonemes."""
    
    syllables = []
    
    # Iterate in reverse (to prioritize onsets over codas)
    i = len(pron) - 1
    while i >= 0:
        
        phon = pron[i]
        
        # Find a vowel
        if re.search('\d', phon): # TODO this generates a warning but seems to work
            
            # Start building the syllable with its nucleus
            stress = int(phon[-1])
            syll = Syllable(stress)            
            syll.nucleus = _get_nuclear_cluster(phon)
            
            # Search forward for coda
            syll.coda = pron[i + 1:]
            
            # Search backward for onset
            j, onset = i - 1, []
            while j >= 0:
                ons_phon = pron[j]
                if (not re.search('\d', ons_phon) # TODO here too
                     or onset and onset[0] in C_CLUSTERS_I.get(ons_phon, [])):
                    onset.insert(0, ons_phon)
                else:
                    break
                j -= 1
            i, syll.onset = j, onset
            
            # Cut pronunciation here to prevent recodifying and add syllable
            pron = pron[:i + 1]
            syllables.insert(0, syll)
        
        # If not a vowel, move on to the next one
        else:
            i -= 1
    
    return syllables

#===========================================================================
# GET PRONUNCIATION
#===========================================================================

def _is_dash(s: str) -> bool:
    """Return True if the given s consists entirely of hyphens."""
    
    return all(c == 's' for c in s)


def _is_hyphenated(s: str) -> bool:
    """Return True iff the given s is hyphenated."""
    
    return '-' in s


def _is_number(s: str) -> bool:
    """Return True iff the given s represents a cardinal number."""
    
    try:
        int(s)
        return True
    except:
        return False


def _is_negative(s: str) -> bool:
    """Return True iff the given s represents a negative number."""
    
    return len(s) > 1 and _is_number(s[1:]) and s[0] == '-'


def _is_ordinal(s: str) -> bool:
    """Return True iff the given s represents an ordinal number."""
    
    return len(s) > 2 and _is_number(s[:-2]) and s[-2:] in {'nd', 'rd', 'st', 'th'}


def _normalize_verbal(s: str) -> str:
    """Return a number spelling normalized in appearance to a compound noun. """
    
    s = s.replace(' ', '-')
    s = s.replace('and ', '')
    return s


def _get_cardinal_pron(s: str) -> list:
    """Return the pronunciation of the spelling of cardinal s."""
    
    verbal = num2words.num2words(float(s))
    return _get_compound_pron(_normalize_verbal(verbal))


def _get_negative_pron(s: str) -> list:
    """Return the pronunciation of the spelling of negative cardinal s."""
    
    verbal = 'minus ' + num2words.num2words(float(s[1:]))
    return _get_compound_pron(_normalize_verbal(verbal))


def _get_ordinal_pron(s: str) -> list:
    """Return the pronunciation of the spelling of ordinal s."""
    
    verbal = num2words.num2words(float(s[:-2]), ordinal=True)
    return _get_compound_pron(_normalize_verbal(verbal))


def _get_compound_pron(s: str) -> list:  
    """Join and return the pronunciation of each piece of hyphenated word s."""
    
    pieces = s.split('-')    
    prons = (_get_word_pron(piece) for piece in pieces)
    return [phon for pron in prons for phon in pron]


def _get_word_pron(s: str) -> list:
    """Return the pronunciation of s."""
    
    return o.PROND.get(s.lower(), [])


def get_pron(s: str) -> list:
    """Return the pronunciation of s, whatever form s has."""
    
    # Is it a number?
    if _is_number(s):
        
        # Is it an ordinal?
        if _is_ordinal(s):
            return _get_ordinal_pron(s)
        
        # Is it a negative cardinal?
        elif _is_negative(s):
            return _get_negative_pron(s)
        
        # Otherwise, it's a positive cardinal
        else:
            return _get_cardinal_pron(s)
    
    # Is it a compound word?
    elif _is_hyphenated(s):
        return _get_compound_pron(s)
    
    # Otherwise, it's a normal word
    else:
        return _get_word_pron(s)

#===============================================================================
# RHYME & SYNONYM ELIGIBILITY
#===============================================================================

def no_syns(s: str) -> bool:
    """Return True iff the given string is ineligible for synonymization."""
    
    return any((_is_dash(s),
                _is_number(s),
                s.lower() in o.SW_SYN,
                s in o.OKAY_PUNCT))


def no_rhyme(s: str) -> bool:
    """Return True iff the given string is ineligible for rhyming."""
    
    return any((_is_dash(s),
                s in o.OKAY_PUNCT,                
                (not o.OPTIONS['STOPWORD_R'] and s in o.SW_RHYME)))
            


#===============================================================================
# PRONUNCIATION SIMILARITY
#===============================================================================

V_WEIGHT_CLOSENESS = .45
V_WEIGHT_BACKNESS = .35
V_WEIGHT_ROUNDED = .2

C_WEIGHT_VOICED = .55
C_WEIGHT_SONORITY = .4
C_WEIGHT_BACKNESS = .05
C_WEIGHT_LATERAL = .65

ONSET_WEIGHT = .2
NUCLEUS_WEIGHT = .4
CODA_WEIGHT = .3
STRESS_WEIGHT = .1

def _cluster_sim(cc1: list, cc2: list, cmp) -> float:
    """
    Return the percentage similarity between two clusters.
    The cmp function passed compares the similarity between two phonemes.
    """    
    
    parallel = list(itertools.zip_longest(cc1, cc2, fillvalue=None))
    length = len(parallel)
    sim = length
    
    for i, (ph1, ph2) in enumerate(parallel):
        
        # If we have two phonemes, simply compare
        if ph1 and ph2:
            sim -= 1.0 - cmp(ph1, ph2)
        
        # Otherwise...
        else:          
            
            # Prepare a recursive call using the entire shorter branch and the
            # remaining items of the longer branch. Base case is 1:1 lengths.                    
            longer = max((cc1, cc2), key=len)
            shorter = min((cc1, cc2), key=len)
            
            subc1 = shorter[:]
            subc2 = longer[i:]
            
            # Get the similarity of these subclusters
            subsim = _cluster_sim(subc1, subc2, cmp)
            
            # This subsimilarity score is diminished
            diff = 1.0 - (subsim * (len(subc2) / len(longer)) ** len(subc2))
            
            # Finally account for the similarity and break
            sim -= diff
            break
    
    return sim / length


def _consonant_sim(co1: str, co2: str) -> float:
    """Return the percentage similarity between two two consonants."""
    
    # Get features
    co1_v, co1_b, co1_s = CONSONANTS[co1]
    co2_v, co2_b, co2_s = CONSONANTS[co2]
    
    # Subtract from 1.0 similarity
    sim = 1.0
    sim -= abs(co1_v - co2_v) / 1 * C_WEIGHT_VOICED
    sim -= abs(co1_b - co2_b) / 5 * C_WEIGHT_SONORITY
    sim -= abs(co1_s - co2_s) / 12 * C_WEIGHT_BACKNESS
    
    # Account for laterality as the only distinction between liquids
    if co1 + co2 in ('RL', 'LR'):
        sim -= 1 * C_WEIGHT_LATERAL
    
    return sim
    
    
def _vowel_sim(vo1: str, vo2: str) -> float:
    """Return the percentage similarity between two vowels."""
    
    # Get features
    vo1_c, vo1_b, vo1_r = VOWELS[vo1]
    vo2_c, vo2_b, vo2_r = VOWELS[vo2]
    
    # Subtract from 1.0 similarity
    sim = 1.0
    sim -= abs(vo1_c - vo2_c) / 6 * V_WEIGHT_CLOSENESS
    sim -= abs(vo1_b - vo2_b) / 4 * V_WEIGHT_BACKNESS
    sim -= abs(vo1_r - vo2_r) / 1 * V_WEIGHT_ROUNDED
    
    return sim


#===============================================================================
# OVERALL PRONUNCIATION SIMILARITY ENGINE
#===============================================================================

SYLL_WEIGHTS_CMPS = ((ONSET_WEIGHT, _consonant_sim),
                     (NUCLEUS_WEIGHT, _vowel_sim),
                     (CODA_WEIGHT, _consonant_sim))


def _short_circuit_pair(item1: object, item2: object) -> float|None:
    """
    Short-circuit the difference check for the pair. Return 1.0 for mismatch,
    0.0 for equivalence, or None for both present but different.
    """
    
    if (bool(item1) + bool(item2)) == 1:
        return 1.0
    
    elif item1 == item2:
        return 0.0
    
    else:
        return None
    

def pron_sim(pr1: list, pr2: list) -> float:
    """Return the percentage similarity between the two lists of syllables."""
    
    # Short-circuit pair
    sc = _short_circuit_pair(pr1, pr2)    
    if sc is not None:
        return 1.0 - sc
    
    else:
    
        # Parallelize and store the length (sim will diminish)
        parallel = list(itertools.zip_longest(pr1, pr2, fillvalue=None))
        length = len(parallel)
        sim = length
        
        # Iterate through syllables
        for sy1, sy2 in parallel:
            
            # Short-circuit syllable
            sc = _short_circuit_pair(sy1, sy2)
            if sc is not None:
                sim -= sc
            
            else:
                # Make iterables out of the syllables
                sg1 = sy1.onset, sy1.nucleus, sy1.coda
                sg2 = sy2.onset, sy2.nucleus, sy2.coda
                
                # Iterate through clusters
                for c1, c2, (weight, cmp) in zip(sg1, sg2, SYLL_WEIGHTS_CMPS):
                    
                    # Short-circuit cluster
                    sc = _short_circuit_pair(c1, c2)
                    if sc is not None:
                        sim -= weight - (sc * weight)
                        
                    else:
                        sim -= weight - (_cluster_sim(c1, c2, cmp) * weight)
                
                # Account for weight difference
                if not o.OPTIONS['IGN_STRESS_L']:
                    stress_diff = (sy1.stress - sy2.stress)
                    sim -= STRESS_WEIGHT - (stress_diff * STRESS_WEIGHT)
        
        return sim / length
