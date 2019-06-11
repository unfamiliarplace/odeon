#===============================================================================
# POEM
# Models a poem and provides formatting and scoring.
#
# EXPORTS
# Vector, Poem, Poem.score
#===============================================================================

import options as o
from manipulation import _rhyme

#===============================================================================
# VECTOR
#===============================================================================

class Vector:
    """Basic data type for representing score vectors."""
    
    def __init__(self, name: str, calc: str, wgt: float, scale: float):
        """
        Initialize with the given name, calculator function, weight, and scale.
        This Vector's average value divided by its scale should be around 1.0.
        The value is initialized as None.
        """
         
        self.name, self.calc, self.weight, self.scale = name, calc, wgt, scale
        self.value = None
        
        
    def __repr__(self) -> str:
        """Return a string representation of this Vector."""
        
        return '{}: {:.2f}'.format(self.name, self.value)
    
#===============================================================================
# POEM
#===============================================================================

class Poem(tuple):
    """
    Extends tuple, adding a calculation of a score representing the technical
    ability of this poem.
    """
    
    def __new__(cls, lines: list) -> 'Poem':
        """Create this Poem and its score vectors."""
        
        p = super().__new__(cls, lines)
        
        p.vectors = [
                     Vector('Rhyme density', '_score_rhyme_density', 5, 10),
                     Vector('Rhyme scheme', '_score_rhyme_scheme', 12, 5),
                     Vector('Unique language', '_score_rarity', 2, 0.00000001),
                     Vector('Poetic language', '_score_poeticness', 3, 1),
                     Vector('Stress consistency', '_score_stress_consistency', 1, 5),
                     Vector('Length consistency', '_score_length_consistency', .5, 5),
                     ]
        
        return p
        
    #===========================================================================
    # TECHNICAL
    #===========================================================================
    
    def __hash__(self) -> int:
        """Return the hash of the tuple of the embedded list."""
        
        return hash(str(self)) + hash(tuple(v.value for v in self.vectors))
    
    
    def __repr__(self) -> str:
        """Return a formatted string representation of this Poem."""
        
        s = ''
        
        for line in self:
            
            # A line's representation is its Words separated by spaces
            joint_line = str(line)
            
            # Lowercase the line if requested
            if o.OPTIONS['LOWERCASE']:
                joint_line = joint_line.lower()
            
            # Capitalize the first letter of the line if requested
            if o.OPTIONS['CAP_START']:
                joint_line = joint_line[0].upper() + joint_line[1:]
            
            s += joint_line + '\n'
        
        # Strip trailing newline
        s = s[:-1] if s.endswith('\n') else s
        
        # If there's punctuation in it, ensure it's properly formatted
        if not o.OPTIONS['STRIP_PUNCT']:
            s = _refold_punctuation(s)
            
        return s
    
    #===========================================================================
    # SCORING HELPERS    
    #===========================================================================
    
    def _get_words(self) -> list:
        """Return all the words in this Poem."""
        
        return [word for line in self for word in line]
    
    
    def _count_distinct_rhymes(self) -> int:
        """Return the number of distinct rhymes in this Poem."""
        
        seen_once, seen_twice = [], []
        for line in self:
            rhyme = line.get_rhyme()
            
            # If a rhyme hasn't been used at least twice, it's not a rhyme.
            if rhyme in seen_once and rhyme not in seen_twice:
                seen_twice.append(rhyme)
            else:
                seen_once.append(rhyme)
                
        return len(seen_twice)
    
    
    def _count_end_rhymes(self) -> int:
        """Return the number of lines that rhyme in this Poem."""
        
        tally = 0
        seen_once, seen_twice = [], []
        for line in self:
            rhyme = line.get_rhyme()
            
            # Our first time seeing this rhyme
            if rhyme not in seen_once:
                seen_once.append(rhyme)
            
            # Our second time seeing it: make sure we count the first time too
            elif rhyme not in seen_twice:
                seen_twice.append(rhyme)
                tally += 2
            
            # Our third time: only accounting for this line now
            else:
                tally += 1
            
        return tally
    
    #===========================================================================
    # SUBSCORERS
    #===========================================================================
    
    def _score_rhyme_density(self) -> float:
        """Return this Poem's score in terms of rhyme density."""
        
        distinct = self._count_distinct_rhymes()
        end = self._count_end_rhymes()
        
        return ((end / distinct) / (1 / len(self))) if distinct else 0.0    
    
    
    def _score_rhyme_scheme(self) -> float:
        """Return this Poem's score in terms of rhyme scheme matching."""
        
        runsets = _rhyme._get_all_best_runsets(self)
        runset = _rhyme._get_best_runset(self, runsets)
        
        if not runset:
            return 0.0
        
        else:
            factors = _rhyme._get_runset_factors(self, runset)
            length, n_runs, n_used, n_unused = factors
            
            return sum([-n_runs, length, n_used, -n_unused])
    
    
    def _score_rarity(self) -> float:
        """Return this Poem's score in terms of lexical rarity."""
        
        words = self._get_words()
        return (sum([word.rarity for word in words]) / len(words))    
    
    
    def _score_poeticness(self) -> float:
        """Return this Poem's score in terms of lexical poeticness."""
        
        words = self._get_words()
        return sum([word.poeticness for word in words]) / len(words)
    
    
    def _score_stress_consistency(self) -> float:
        """Return this Poem's score in terms of line stress consistency."""
        
        if not o.OPTIONS['M']:
            return 0.0
        
        else:
            cmp = lambda line: line.get_n_stresses()            
            lower, upper = min(self, key=cmp), max(self, key=cmp)
            
            return 1 / (abs(len(upper) - len(lower)) + 1)
        
    
    def _score_length_consistency(self) -> float:
        """Return this Poem's score in terms of line length consistency."""
        
        if not o.OPTIONS['M']:
            return 0.0
        
        else:          
            lower, upper = min(self, key=len), max(self, key=len)
                    
            return 1 / (abs(len(upper) - len(lower)) + 1)
        
    
    #===========================================================================
    # MAIN SCORER
    #===========================================================================
    
    def _calculate_vectors(self):
        """Calculate and update this Poem's score vectors."""
        
        for vector in self.vectors:
            calc = getattr(self, vector.calc)            
            vector.value = calc() / vector.scale
    
    
    def score(self) -> tuple:
        """
        Return a tuple: (sum of calculated score vectors, score vectors).
        If a verbose score has not been requested, condense vectors to 'Score'.
        """
        
        self._calculate_vectors()
        
        # Get the total score and make it a vector (for polymorphism's sake)
        score = sum(v.value * v.weight for v in self.vectors)
        total_vector = Vector('Score', None, None, None)
        total_vector.value = score
        
        if o.OPTIONS['VERBOSE_SCORE']:
            return (score, [total_vector] + self.vectors)
        
        else:           
            return (score, [total_vector])
    
    
#===============================================================================
# MODULE-LEVEL FUNCTIONS
#===============================================================================

def _refold_punctuation(s: str) -> str:
    """Return s with all punctuation attached to the preceding word."""
    
    # Remove space before punctuation; ensure it's not at the start of a line
    for p in o.OKAY_PUNCT:
        s = s.replace(' {}'.format(p), p)
        s = s.replace('\n{}'.format(p), '{}\n'.format(p))
    
    s = s.replace('\n ', '\n')
    s = s[:-1] if s.endswith('\n') else s
    
    # If we removed a line, it's possible to have lost ending punctuation
    if o.LAST_WAS_PUNCT and s[-1] not in o.OKAY_PUNCT:
        s += '.'
        
    return s
