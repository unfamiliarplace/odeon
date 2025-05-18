#===============================================================================
# OPTIONS
# Stores all cross-module options and constants for the program.
#
# EXPORTS
# LOG, RELDIR
# SW_SYN, SW_RHYME, SW_ELLIPSIS, OKAY_PUNCT
# PROND, SYND, C_POEMS, C_PROSE, FD_POEMS, FD_PROSE
# POEMS_BASE, PROSE_BASE, PROND_FNAME, SYND_FNAME
# O_TABLE, OPTIONS, PRESETS
#===============================================================================

import os
from collections import OrderedDict as ODict
from language import _stopwords as sw
from controller._option import OptionBool, OptionStartInf, OptionRange
from controller._option import OptionODict, Preset

#===============================================================================
# ENVIRONMENT
#===============================================================================

# Logger
LOG = None

# Relative directory, for finding resources
RELDIR = os.path.dirname(__file__)

# Locations of things in the data subfolder
POEMS_BASE = RELDIR + '/_data/poems/'
PROSE_BASE = RELDIR + '/_data/prose/'
PROND_FNAME = RELDIR + '/_data/pronunciation_dictionary/cmudict-0.7b-cdn.txt'
SYND_FNAME = RELDIR + '/_data/synonym_dictionary/karo-synonyms.txt'

#===============================================================================
# RESOURCES: Constants for dictionaries, corpora, etc.
#===============================================================================

# Stopword groupings
SW_SYN, SW_RHYME, SW_ELLIPSIS = sw.SYN, sw.RHYME, sw.ELLIPSIS

# Allowable punctuation
OKAY_PUNCT = set(".,;:!?")
LAST_WAS_PUNCT = False

# Pronunciation and synonym dictionaries
PROND = {}
SYND = {}

# Poetry and prose corpora
C_POEMS = None
C_PROSE = None

# Poetry and prose FreqDists
FD_POEMS = None
FD_PROSE = None

def _find_subgenres(basedir: str) -> list:
    """
    Return a list of subgenres derived from folder names in the given base
    directory. The list contains tuples of the form (nice name, real name).
    """
    
    dirs = list(os.walk(basedir))[0][1]
    return [(d.replace('_', ' ').title(), d) for d in dirs]

#===============================================================================
# OPTIONS TABLE: The main table of options for poem generation and formatting.
#===============================================================================

# The Nones in this table are for spacing options.
O_TABLE = (
           #====================================================================
           # FORMATTING
           #====================================================================
           OptionBool('CUST_F', True,
                      'Change formatting'),
           OptionBool('LOWERCASE', False,
                      'Lowercase the text',
                      deps='__CUST_F__'),
           OptionBool('CAP_START', True,
                      'Capitalize the start of each line',
                      deps='__CUST_F__'),
           OptionBool('STRIP_PUNCT', False,
                      'Strip punctuation',
                      deps='__CUST_F__'),
           
           None,
           #====================================================================
           # SCORE
           #====================================================================
           OptionBool('VERBOSE_SCORE', False,
                      'Show a detailed score breakdown for each poem'),
           
           None,
           #====================================================================
           # RHYME
           #====================================================================
           OptionBool('R', True,
                      'Use rhyme'),
           OptionBool('CUST_R', True,
                      'Customize rhyme options',
                      deps='__R__'),
           OptionBool('ORPHAN_R', True,
                      'Allow an orphaned (unrhyming) end line',
                      deps=' __CUST_R__ and __R__'),
           OptionBool('MATCH_R_S', False,
                      'Poem must match a rhyme scheme',
                      deps='__CUST_R__ and __R__'),
           OptionBool('CUT_LINES_R_S', False,
                      'Cut lines to make poems match a rhyme scheme',
                      deps='__CUST_R__ and __R__'),
           OptionStartInf('N_SELF_RHYME', 0,
                          'How many times can a word rhyme with itself',
                          deps='__CUST_R__ and __R__'),
           OptionRange('RHYME_DIFF', 0,
                      'What % slant can rhymes be',
                      deps='__CUST_R__ and __R__',
                      range=range(0, 41)),
           OptionBool('IGN_STRESS_L', True,
                      'Ignore subtle stress level when rhyming',
                      deps='__CUST_R__ and __R__ '),
           OptionBool('HARD_RHYME', False,
                      'Aim for unusually long, but fewer, rhymes',
                      deps='__CUST_R__ and __R__ and __RHYME_DIFF__ >= 25'
                      ' and __IGN_STRESS_L__'),
           OptionBool('STOPWORD_R', False,
                      'Rhyme on stopwords',
                      deps='__CUST_R__ and __R__'),
           OptionBool('ONE_R', False,
                      'Limit to one intentional rhyming sound',
                      deps='__CUST_R__ and __R__ and not __RHYME_DIFF__'),
           
           None,
           #====================================================================
           # METER
           #====================================================================
           OptionBool('M', True,
                      'Use meter'),
           OptionBool('CUST_M', True,
                      'Customize meter options',
                      deps='__M__'),
           OptionBool('RHYTHM', True,
                      'Use rhythm as well as strict meter',
                      deps='__CUST_M__ and __M__'),
           OptionBool('ORPHAN_M', True,
                      'Allow an orphaned (unmetrical) end line',
                      deps='__CUST_M__ and __M__'),
           OptionBool('FLATTEN_STRESS_M', False,
                      'Flatten stress for meter',
                      deps='__CUST_M__ and __M__'),
           OptionBool('ENJAMB', True,
                      'Allow enjambment',
                      deps='__CUST_M__ and __M__'),
           
           None,
           #====================================================================
           # RHYME & METER INTERFACE
           #====================================================================
           
           OptionBool('RHYMELESS_R', False,
                      'Allow lines without meter, for the sake of rhyme',
                      deps='__CUST_R__ and __CUST_M__ and __R__ and __M__'),
           OptionBool('RHYMELESS_M', False,
                      'Allow lines without rhymes, for the sake of meter',
                      deps='__CUST_R__ and __CUST_M__ and __R__ and __M__'),
           
           None,
           #====================================================================
           # SYNONYMS
           #====================================================================
           OptionBool('S', True,
                      'Use more poetic synonyms of words'),
           OptionBool('CUST_S', True,
                      'Customize synonym options',
                      deps='__S__'),
           OptionRange('SYN_FLEX', 15,
                       'What percentage of homonyms should be considered',                       
                       deps='__CUST_S__ and __S__ ',
                       range=range(1, 101)),
           OptionRange('SYN_MAX', 2,
                       'How many synonyms should each word be limited to',                       
                       deps='__CUST_S__ and __S__',
                       range=range(1, 4)),
           OptionBool('BEST_VARIANTS', True,
                      'Use only the most poetic and rare variants (far faster)',
                      deps='__CUST_S__ and __S__'
                      ),
           OptionODict('C_PO', '',
                       'Which poetry genre should be used',
                       deps='__CUST_S__ and __S__',
                       odict=ODict([('All', '')] + 
                                    _find_subgenres(POEMS_BASE))),
           OptionODict('C_PR', '',
                       'Which prose genre should be used',  
                       deps='__CUST_S__ and __S__',
                       odict=ODict([('All', '')] + 
                                    _find_subgenres(PROSE_BASE))),
           
           None,
           #====================================================================
           # STOPWORDS
           #====================================================================
           OptionBool('NO_STOP', False,
                      'Remove grammatical words to be elliptical'),
           
           None,
           #====================================================================
           # RESOURCES
           #====================================================================
           OptionBool('LOCAL_PROND', True,
                      'Use a local copy of the pronunciation dictionary'
                      ' (faster, Canadianized)',
                      deps='__R__ or __M__'),
           
           OptionBool('LOCAL_SYND', False,
                      'Use a local copy of the synonym dictionary'
                      ' (faster, but worse quality)',
                      deps='__S__'),
           )


# Initialize options with defaults. They will be overriden by user or presets.
OPTIONS = {o.name: o.default for o in O_TABLE if o}

#===============================================================================
# PRESETS
#===============================================================================

# Basic list of options to copy for preset making. Any not set remain default

'''
# ID # explanation # default # range ? # dependency ?
 
# formatting
('LOWERCASE', val), # lowercase # False
('CAP_START', val), # lines start capitalized # True
('STRIP_PUNCT', val), # False
 
# scoring
('VERBOSE_SCORE', val), # score breakdown # False

# rhyming ('all dependent on R)
('R', val), # use rhyme # True
('ORPHAN_R', val), # leave unrhyming end # False
('MATCH_R_S', val), # poem must match rhyme scheme # False
('CUT_LINES_R_S', val), # can cut lines to match rhyme scheme # False
('N_SELF_RHYME', val), # times a word can rhyme with itself # 0 # 0 to inf
('RHYME_DIFF', val), # % slant a rhyme can be # 0 # 0 to 40
('IGN_STRESS_L', val), # ignore stress level # True
('HARD_RHYME', val), # aim for longest possible rhymes # False # IGN_STRESS_L
('STOPWORD_R', val), # prevent stopword rhyming # True
('ONE_R', val), # only one rhyming sound # False

# meter ('all dependent on M)
('M', val), # use meter # True
('RHYTHM', val), # rhythm allowed # True
('ORPHAN_M', val), # leave unmetrical end # True
('FLATTEN_STRESS_M', val), # ignore stressed/unstressed in feet # False
('ENJAMB', val), # let feet carry across lines # True
('RHYMELESS_M', val), # allow meter break even if no rhyme # True

# synonyms ('all dependent on S)
('S', val), # use synonyms # True
('SYN_FLEX', val), # % of homonymic meanings # 15 # 0 to 100
('SYN_MAX', val), # max synonyms per word # 2 # 1 to 3
('BEST_VARIANTS', val), # only most poetic and rarest variants # True
('C_PO', val), # poetry genre # '' ('all)
('C_PR', val), # prose genre # '' ('all)

# stopwords
('NO_STOP', val), # remove stopwords # False

# resources
('LOCAL_PROND', val), # local pron dict instead of NLTK # True # R or M
('LOCAL_SYND', val), # local syn dict instead of NLTK # False # S
'''


PRESETS = (
           Preset('Default (rhyme, rhythm, synonyms)',
                  ODict((o.name, o.default) for o in O_TABLE if o)),
           
           Preset('Rhyme and rhythm',
                  ODict((                          
                        ('R', True), # use rhyme # True
                        ('M', True), # use meter # True
                        ('S', False), # use synonyms # True
                        ))),
           
           Preset('Rhyme and rhythm (flexible)',
                 ODict((                          
                        ('R', True), # use rhyme # True
                        ('RHYME_DIFF', 25),
                        ('RHYMELESS_R', True),
                        ('M', True), # use meter # True
                        ('RHYTHM', True), # rhythm allowed # True
                        ('S', False), # use synonyms # True
                        ))),
           
           Preset('Just rhyme',
                  ODict((
                        ('R', True), # use rhyme # True
                        ('M', False), # use meter # True
                        ('S', False), # use synonyms # True
                        ))),
           
           Preset('Just meter',
                  ODict((   
                        ('R', False), # use rhyme # True
                        ('M', True), # use meter # True
                        ('RHYTHM', False), # rhythm allowed # True
                        ('S', False), # use synonyms # True
                        ))),
           
           Preset('Meter and rhythm',
                  ODict((   
                        ('R', False), # use rhyme # True
                        ('M', True), # use meter # True
                        ('RHYTHM', True), # rhythm allowed # False
                        ('S', False), # use synonyms # True
                        ))),
           
           Preset('Rhythm & crazy synonyms',
                  ODict((
                         # formatting
                        ('LOWERCASE', True), # lowercase # False
                        ('CAP_START', False), # lines start capitalized # True
                        ('STRIP_PUNCT', True), # False
                        
                        # rhyming ('all dependent on R)
                        ('R', False), # use rhyme # True
                        
                        # meter ('all dependent on M)
                        ('M', True), # use meter # True
                        ('RHYTHM', True), # rhythm allowed # False
                        ('ORPHAN_M', True), # leave unmetrical end # True
                        ('ENJAMB', True), # let feet carry across lines # True
                        
                        # synonyms ('all dependent on S)
                        ('S', True), # use synonyms # True
                        ('SYN_FLEX', 100), # % of homonymic meanings # 15 # 0 to 100
                        ('SYN_MAX', 3), # max synonyms per word # 2 # 1 to 3
                        ('BEST_VARIANTS', False), # only most poetic and rarest variants # True
                        
                        # stopwords
                        ('NO_STOP', True), # remove stopwords # False
                         ))),
           
           Preset('Rhyme & crazy slant',
                  ODict((                        
                        # rhyming ('all dependent on R)
                        ('R', True), # use rhyme # True
                        ('ORPHAN_R', True), # leave unrhyming end # False
                        ('N_SELF_RHYME', 1), # times a word can rhyme with itself # 0 # 0 to inf
                        ('RHYME_DIFF', 40), # % slant a rhyme can be # 0# 0 to 40
                        ('IGN_STRESS_L', True), # ignore stress level # True
                        ('STOPWORD_R', False), # prevent stopword rhyming # True
                        
                        # meter ('all dependent on M)
                        ('M', False), # use meter # True
                        
                        # synonyms ('all dependent on S)
                        ('S', False), # use synonyms # True
                         ))),
           
           Preset('Cut to rhyme',
                  ODict((                        
                        # rhyming ('all dependent on R)
                        ('R', True), # use rhyme # True
                        ('ORPHAN_R', True), # leave unrhyming end # False
                        ('MATCH_R_S', False), # poem must match rhyme scheme # False
                        ('CUT_LINES_R_S', False), # can cut lines to match rhyme scheme # False
                        ('N_SELF_RHYME', 0), # times a word can rhyme with itself # 0 # 0 to inf
                        ('RHYME_DIFF', 0), # % slant a rhyme can be # 0 # 0 to 40
                        ('IGN_STRESS_L', True), # ignore stress level # True
                        ('HARD_RHYME', False), # aim for longest possible rhymes # False # IGN_STRESS_L
                        ('STOPWORD_R', False), # prevent stopword rhyming # True
                        ('ONE_R', False), # only one rhyming sound # False
                        
                        # meter ('all dependent on M)
                        ('M', False), # use meter # True
                        
                        # synonyms ('all dependent on S)
                        ('S', False), # use synonyms # True
                         ))),
           )
