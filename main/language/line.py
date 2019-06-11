#===============================================================================
# LINE
# Models a line (an individual verse) in a poem.
#
# EXPORTS
# Line, Line.get_rhyme, Line.get_n_stresses
#===============================================================================

from manipulation._meter import get_symbolic_string, SS, EI

class Line(list):
    """Extends list, storing Words and adding hashing and rhyming."""

    def __init__(self, *args) -> None:
        """Initialize this Line."""
        
        super().__init__(args) if args else super().__init__    
    
    
    def __repr__(self) -> str:
        """Return the Words in this Line, separated by spaces."""
        
        return ' '.join(self)
    
    
    def get_rhyme(self) -> list:
        """Return the rhyme of the last word of this line."""
        
        return self[-1].get_rhyme_segment() if self else []
    
    
    def get_n_stresses(self) -> int:
        """Return the number of stresses in this line."""
        
        symbolic = get_symbolic_string(self)
        return symbolic.count(SS) + (symbolic.count(EI) // 2)
