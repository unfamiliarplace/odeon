#===============================================================================
# POEMS
# Functions for breaking a flat list of words into lines and then poems.
#
# EXPORTS
# get_poems
#===============================================================================

import options as o
from manipulation._rhyme import get_all_rhymesets
from manipulation._meter import get_all_metersets, get_symbolic_string
from manipulation._meter import get_foot_match, US, SS, EI

from language.poem import Poem
from language.line import Line
from language.word import Word

import itertools

#===============================================================================
# BREAKING LINES
#===============================================================================

def _break_rhyme(word: Word, rhymeset: set, words_rhymed: dict) -> bool:
    """Return True iff this is an okay word to break on in terms of rhyme."""
    
    return ((o.OPTIONS['M'] and o.OPTIONS['RHYMELESS_M'])
            or (word in rhymeset
                and words_rhymed.get(word, 0) <= o.OPTIONS['N_SELF_RHYME']))
    

def _break_meter(line_meter: str, foot: str, FPL: int, enjambed: bool) -> bool:
    """Return True iff this is an okay word to break on in terms of meter."""
    
    # If our first syllable is claimed by an enjambed word, ignore it
    if enjambed:
        line_meter = line_meter[1:]
    
    # If this is a rhythm meterset, just count stresses or syllables
    if foot in (US, SS):
        return line_meter.count(foot) + line_meter.count(EI) >= FPL
    
    # Otherwise do the foot matching
    else:
        match = get_foot_match(line_meter, foot)
        return match and len(match.group()) >= len(foot * FPL)


def _is_illegal_enjambment(foot: str, extra_sylls: str) -> bool:
    """Return True iff the extra syllables represent illegal enjambment."""
    
    return not ((not o.OPTIONS['M'])
                or (o.OPTIONS['ENJAMB']
                    and len(extra_sylls) <= 1
                    and (foot in (US, SS) or foot.startswith(extra_sylls))))
    

def _get_extra_sylls(line_meter: str, foot: str, feet_per_line: int) -> str:
    """Return the number of syllables left over after the foot requirement."""
    
    if foot in (US, SS):
        end = line_meter.rfind(foot)
        return line_meter[end + 1:]
    
    else:
        n = len(line_meter) - len(foot * feet_per_line)
        return line_meter[n:] if n else ''
    

def _can_orphan() -> bool:
    """Return True iff an orphaned line can be produced."""
    
    if o.OPTIONS['R'] and o.OPTIONS['M']:
        return o.OPTIONS['ORPHAN_R'] and o.OPTIONS['ORPHAN_M']
    
    elif o.OPTIONS['R']:
        return o.OPTIONS['ORPHAN_R']
    
    else:
        return o.OPTIONS['ORPHAN_M']


def _get_lines(words: list, rhymeset: set, meterset: set) -> list:
    """Return a list of lines broken according to the given rhymes and meter."""
    
    def _can_break() -> bool:
        """Helper to determine whether a word is okay to break on."""
                
        # Check appropriate conditions depending on how we're breaking
        if o.OPTIONS['R'] and o.OPTIONS['M']:
            return (_break_rhyme(word, rhymeset, words_rhymed)
                    and _break_meter(line_meter, foot, feet_per_line, enjambed))
        
        elif o.OPTIONS['R']:
            return _break_rhyme(word, rhymeset, words_rhymed)
        
        else:
            # Never break just for meter before an unpronounceable word.
            if (i < len(words) - 1) and (not words[i+1].pron):
                return False
            return _break_meter(line_meter, foot, feet_per_line, enjambed)        
    
    foot, feet_per_line = meterset
    
    lines = []
    words_rhymed = {}
    
    # Begin constructing a line
    line = Line()
    line_meter = ''
    enjambed = False
    
    for i, word in enumerate(words):
        
        # Accumulate line        
        line.append(word)        
        line_meter += get_symbolic_string([word])
        
        # Break
        if _can_break():
            
            # Get leftover syllables and check enjambment
            extra_sylls = _get_extra_sylls(line_meter, foot, feet_per_line)    
            if _is_illegal_enjambment(foot, extra_sylls):
                return []
            
            else:            
                # Register the rhyme
                words_rhymed[word] = words_rhymed.get(word, 0) + 1
                
                # Add and reset the line
                lines.append(line)
                line = Line()
                line_meter = extra_sylls
                enjambed = bool(extra_sylls)
    
    # Catch a last unbroken line if allowed
    if line and _can_orphan():
        lines.append(line)
    
    return lines


#===============================================================================
# GENERATING POEMS
#===============================================================================

def _get_rhyme_meter_pairs(words: list) -> set:
    """Return a set of tuples of of combinations of (rhymeset, meterset)."""
    
    # Get rhymesets or dummies (for proper product creation)
    rhymesets = get_all_rhymesets(words) if o.OPTIONS['R'] else {(Word('I'))}
    metersets = get_all_metersets(words) if o.OPTIONS['M'] else {(SS, 1)}
    
    return itertools.product(rhymesets, metersets)


def get_poems(words: list) -> list:
    """Return a list of Poems made by splitting the given words into lines."""
    
    poems = set()
    
    # If we're not breaking on rhyme or meter, we have nothing to break on
    if not (o.OPTIONS['R'] or o.OPTIONS['M']):
        return poems
    
    # Otherwise we're in business
    else:
        # All possible pairs of (rhymeset, meterset)
        rhyme_meter_pairs = _get_rhyme_meter_pairs(words)
    
        # For each pair, add the poem it yields
        for pair in rhyme_meter_pairs:
            lines =_get_lines(words, *pair)
            poem = Poem(lines)
            poems |= {poem} if poem else set()
    
    return poems
    