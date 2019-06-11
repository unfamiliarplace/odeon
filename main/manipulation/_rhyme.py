#===============================================================================
# RHYME
# Functions for making poems by rhyme and matching to rhyme schemes.
#
# EXPORTS
# get_all_rhymes, filter_poems
#===============================================================================

from main.language.poem import Poem
import itertools, re
import main.options as o

#===============================================================================
# RHYME: Functions for arranging words by their rhyming qualities.
#===============================================================================
    
SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
SCHEMES = (
       'AA',
       'A.',
       '.A',
       'A.A',
       'ABAB',
       'AABB',
       'AB.B',
       'AAA.',
       'AABAB',
       'ABABA',
       'ABAAAB',
       'ABBCCA',
       'AAABCCCB',
       'ABABCDCDEFEFGG',
       )

#===============================================================================
# TOOLS
#===============================================================================

def _is_subsumed(one: object, mass: object) -> bool:
    """Return True iff the given hashable iterable is subsumed by the mass."""
    
    cast = set(one)
    return any(cast.issubset(set(other)) for other in mass)

#===============================================================================
# IDENTIFYING RHYMES
#===============================================================================

def _get_all_base_rhymes(words: list) -> set:
    """Return the set of rhyme tuples that can be formed from words."""
    
    all_rhymes = set()
    for i, word in enumerate(words):
        
        rhymes = word.get_rhyme_matches(words[i:])
        if not _is_subsumed(rhymes, all_rhymes):
            all_rhymes |= {rhymes}
    
    return all_rhymes


def _is_valid_rhymeset(rhymes: tuple) -> bool:
    """
    Return True for the given rhyme tuple iff
        (a) There is more than one distinct rhyme
        (b) There is only one distinct rhyme, but there is more than one
            instance*, and exact (same word) rhymes are allowed
                    * Because the word itself is included.
    """
    
    return (len(set(rhymes)) > 1
            or (len(rhymes) > 1 and o.OPTIONS['N_SELF_RHYME'] > 0))
    

def _get_rhyme_combinations(all_rhymes: set) -> set:
    """Return all combinations of the given set of rhymes."""
    
    new_rhymes = set()
    
    for i in range(len(all_rhymes) + 1):
        for subset in itertools.combinations(all_rhymes, i + 1):
            flat = (word for rhymes in subset for word in rhymes)
            new_rhymes |= {tuple(sorted(flat))}
    
    return new_rhymes


def get_all_rhymesets(words: list) -> set:
    """Return the set of valid rhyme tuples for the given words."""
    
    all_rhymes = _get_all_base_rhymes(words)
    all_rhymes = set(filter(_is_valid_rhymeset, all_rhymes))
    
    # If single rhyme is selected, each poem will only rhyme on one tuple
    # Otherwise, each tuple is expanded to its combinations
    if not o.OPTIONS['ONE_R']:
        all_rhymes = _get_rhyme_combinations(all_rhymes)
    
    return all_rhymes

#===============================================================================
# MATCHING RHYME SCHEMES
#===============================================================================

def _get_symbolic_poem(poem: Poem, start: int=0) -> str:
    """Convert the given Poem to its rhyme scheme (a string of symbols)."""
    
    rhyme_to_symbol = {}
    symbols = SYMBOLS
    symbolic_poem = ''
    
    for line in poem[start:]:
        
        # Identify this line's rhyme
        rhyme = line.get_rhyme()
        
        if rhyme:
            rhyme = tuple(rhyme)
        
            # If the rhyme has not been seen yet, reserve a new symbol for it
            # (if there are any left) and shift symbols along
            if rhyme not in rhyme_to_symbol.keys():
                if symbols:
                    symbol = symbols[0]
                    symbols = symbols[1:]
                    
                # Reserve the symbol, and add it to the symbolic poem
                rhyme_to_symbol[rhyme] = symbol    
                symbolic_poem += symbol
            
            # If the rhyme has been seen, add the symbol that stands for it
            else:
                symbolic_poem += rhyme_to_symbol[rhyme]
            
    return symbolic_poem
    

def _get_scheme_runsets(poem: Poem, scheme: str) -> tuple:
    """
    Return a list of runsets for the given Poem and the given rhyme scheme.
    A runset is a list of tuples whose items are the start and end indices
    of a complete run of the rhyme scheme.
    """
    
    runsets = []
    offset = 0
    symbolic_poem = _get_symbolic_poem(poem, offset)
    
    # Shift the symbolic poem to get each possible assignment of symbols
    # (e.g. to match poem ABBCB to scheme AABA: symbolize after first line)
    while symbolic_poem:
        
        # Find all runs
        runset = []
        matches = re.finditer(scheme, symbolic_poem)
        for match in matches:
            runset.append((match.start(), match.end()))
        
        # If a runset was found (and is not a subet of another runset), add it
        if runset and not _is_subsumed(runset, runsets):
            runsets.append(runset)
        
        # Keep track of the offset (lines "skipped" during symbolization)
        # Move the poem along till we are out of lines to symbolize
        offset += 1
        symbolic_poem = _get_symbolic_poem(poem, offset)
        
    return runsets


def _get_runset_factors(poem: Poem, runset: list) -> tuple:
    """Return a tuple: (scheme length, # of runs, used lines, unused lines)."""
    
    length = 0
    used = 0
    for start, end in runset:
        length = end - start
        used += length
    return length, len(runset), used, len(poem) - used


def _get_runset_cmp(poem_runset: tuple) -> tuple:
    """
    Arrange runset factors in the (poem, runset) tuple poem_runset such that
    it sorts meaningfully: fewest runs, longest scheme, fewest unused lines.
    """
    
    poem, runset = poem_runset
    length, n_runs, _, n_unused = _get_runset_factors(poem, runset)
    return -n_runs, length, -n_unused


def _get_best_runset(poem: Poem, runsets: list) -> list:
    """Get the best runset for the given Poem and its runsets."""
    
    if runsets:
        paired = ((poem, runset) for runset in runsets)
        sorted_pairs = sorted(paired, key=_get_runset_cmp, reverse=True)
        
        if sorted_pairs:
            return sorted_pairs[0][1]


def _get_all_best_runsets(poem: Poem) -> list:
    """Get the best runsets for the Poem for each rhyme scheme."""
    
    # Get the runsets for each scheme; omit any unproductive ones
    all_sets = (_get_scheme_runsets(poem, scheme) for scheme in SCHEMES)
    all_sets = (runsets for runsets in all_sets if runsets)
    
    # Get each scheme's best runset; get the best of those
    if all_sets:    
        bests = (_get_best_runset(poem, runsets) for runsets in all_sets)        
        return bests
    

#===============================================================================
# POEM FILTERING
#===============================================================================

def _is_perfect_scheme_match(poem: Poem) -> bool:
    """Return True iff the given Poem perfectly matches any rhyme scheme."""
    
    # Get the overall best scheme runsets
    runsets = _get_all_best_runsets(poem)
    
    # A poem is a perfect match if there are no unused lines (4th rs factor)
    return any(not _get_runset_factors(poem, runset)[3] for runset in runsets)


def _cut_to_matching(poem: Poem) -> 'Iterable[Poem]':
    """
    Yield cut versions of the given Poem using only lines that match the best
    runset for each scheme.
    """
    
    # Get the overall best scheme runsets
    best_runsets = _get_all_best_runsets(poem)
    
    for runset in best_runsets:
        
        # Get all lines that match runs of the scheme
        lines = []
        for start, end in runset:
            lines += list(poem[start:end])
        
        yield Poem(lines)
        

def _cut_to_rhyming(poem: Poem) -> Poem:
    """
    Yield a cut version of the given Poem using only lines that rhyme with
    other lines.
    """
    
    lines = []
    
    for line in poem:
        if any(line.get_rhyme() == other.get_rhyme()
               for other in poem if other is not line):
            lines.append(line)
            
    return Poem(lines)


def filter_poems(poems: list) -> list:
    """
    Reduce poems to those that match rhyme schemes, or are cut to match rhyme
    schemes, and that are without orphans, according to the user's options.
    """
    
    # Reduce poems to their rhyming lines
    if not o.OPTIONS['ORPHAN_R']:
        poems = (_cut_to_rhyming(poem) for poem in poems)
        
    # Reduce poems to only lines that match a rhyme scheme (if any)
    if o.OPTIONS['CUT_LINES_R_S']:
        poems = (_cut_to_matching(poem) for poem in poems)
        poems = (poem for poems in poems for poem in poems if poem)
    
    # Narrow down to only poems that perfectly match a rhyme scheme
    if o.OPTIONS['MATCH_R_S']:
        poems = filter(_is_perfect_scheme_match, poems)
    
    return poems
