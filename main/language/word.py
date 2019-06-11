#===============================================================================
# WORD
# Models a word, providing access to pronunciation and synonym functions.
#
# EXPORTS
# Word, Word.pron, Word.rarity, Word.poeticness
# Word.get_rhyme_segment, Word.rhymes, Word.get_rhyme_matches
#===============================================================================

import options as o
from language._pronunciation import Syllable, get_pron, syllabify
from language._pronunciation import no_rhyme, no_syns, pron_sim
from language._synonym import get_poeticness, get_rarity

class Word(str):
    """Extends str, adding functionality for pronunciation and synonyms."""

    def __new__(cls: type, word: str, use_local_prond: bool=True) -> None:
        """Return a new Word with possible pronunciation, poeticness, rarity."""
        
        s = super().__new__(cls, word)
        
        # Defaults in case the resources are not loaded
        s.pron, s.poeticness, s.rarity = [], 0.0, 0.0
        s.no_syns, s.no_rhyme = False, False
        
        # Add the pronunciation if needed
        if o.OPTIONS['R'] or o.OPTIONS['M']:
            
            # If it's unparseable (e.g. mixed digits & letters), ignore it
            try:
                s.pron = get_pron(s)
                s.pron = syllabify(s.pron)
                
            except:
                return None
            
            # Determine eligibility for rhyming
            s._no_rhyme = no_rhyme(s)
        
        # Add the poeticness and rarity if needed
        if o.OPTIONS['S']:
            s.poeticness = get_poeticness(s)
            s.rarity = get_rarity(s)
            
            # Determine eligibiltiy for synonymization
            s._no_syns = no_syns(s)
        
        return s
    
    #===========================================================================
    # TECHNICAL
    #===========================================================================
    
    def __eq__(self, other) -> bool:
        """Return True iff this lowercased embedded str is equal to other's."""  
              
        return self.lower() == other.lower()
    
    
    def __hash__(self) -> int:
        """Return the hash of the embedded str.""" 
               
        return hash(str(self.lower()))
    
    
    def __repr__(self) -> str:
        """Return a string representation of the Word."""     
           
        return 'Word({})'.format(self)
    
    #===========================================================================
    # PRONUNCIATION
    #===========================================================================    
    
    def _find_peak(self, ix: int= -1, cat=Syllable._is_stress) -> int:
        """
        Return the index of the ix-th salient syllable. Default: stressed.
        If there are no stressed syllables, just give the ix-th syllable.
        """
        
        if self.pron:
            
            enp = [(i, peak) for i, peak in enumerate(self.pron) if cat(peak)]
            
            if enp:
                return enp[ix][0]
            else:
                return self._find_peak(ix, cat=lambda *args: True)
        
    #===========================================================================
    # RHYME
    #===========================================================================
    
    def get_rhyme_segment(self) -> list:
        """
        Return the rhyming portion: a salient syllable through the end.
        Set the start (the index of the "last salient syllable").
        """
        
        # Short-circuit
        if self._no_rhyme:
            return []
            
        # Identify the start
        if o.OPTIONS['HARD_RHYME']:
            start = 0
        else:
            start = -1
        
        # Get the base rhyme
        i = self._find_peak(start)
        r = self.pron[i:]
        
        if r:
                    
            # Return a version without the onset for the first syllable
            f = r[0]
            return [Syllable(f.stress, [], f.nucleus, f.coda)] + r[1:]
        
    
    def rhymes(self, other) -> bool:
        """Return True iff this Word rhymes with the given Word."""
        
        # Collect rhymes
        r1 = self.get_rhyme_segment()
        r2 = other.get_rhyme_segment()
        
        # If at least one is unpronounceable
        if not (r1 and r2):
            return False
        
        # If both are pronounceable
        else:
            # Get the threshold -- 0 if they must be exact rhymes
            threshold = o.OPTIONS['RHYME_DIFF']
            
            sim = pron_sim(r1, r2)
            return sim >= (1.0 - (threshold / 100))
    
    
    def get_rhyme_matches(self, words: list) -> tuple:
        """Return a tuple of the Words in words that rhyme with this word."""
        
        # Include self
        return tuple(w2 for w2 in words if self.rhymes(w2))
    
    #===========================================================================
    # SYNONYMS
    #===========================================================================
        
    def get_synonyms(self) -> set:
        """Return the synonyms of this Word, if it is not a stopword."""
        
        # Short-circuit
        if self._no_syns:
            return set()
        
        else:
            syns = o.SYND.get(self.lower(), set())
            syns = (Word(syn) for syn in syns)
            return set(syn for syn in syns if syn)
        

    def get_rare_synonyms(self) -> set:
        """Return the synonyms of this Word that are equally or more rare."""
           
        return set(syn for syn in self.get_synonyms()
                if syn.rarity >= self.rarity)
        
    
    def get_poetic_synonyms(self) -> set:
        """Return the synonyms of this Word that are equally or more poetic."""
        
        return set(syn for syn in self.get_synonyms()
                if syn.poeticness >= self.poeticness)
        