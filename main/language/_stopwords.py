#===============================================================================
# STOPWORDS
# Groupings of stopwords for various purposes.
# 
# EXPORTS
# SW_SYNS, SW_RHYME, SW_ELLIPSIS
#===============================================================================

from nltk.corpus import stopwords

#===============================================================================
# SET UP BASE
#===============================================================================

_BASE = set(stopwords.words('english'))

#===============================================================================
# DEFAULT NLTK STOPWORDS, LOOSELY GROUPED
#
# be being am is are was were been
# do doing does did
# have having has had
# where when who which why what how whom
# can should will
# a an the
# all any some each both most few
# these those this that
# i you he she it we they
# me him them
# my your our his her their yours ours his hers theirs its
# myself yourself yourselves himself herself itself ourselves themselves
# by through from at after between of up for below over under out above before
# further until against down off out in on into about
# as to or and but because too not so no if nor on than then there here
# just only very such other while with now more again once same own during
# s t don
#===============================================================================

#===============================================================================
# CUSTOM GROUPINGS
#===============================================================================

def _modify_base(base: set, remove: str='', add: str='') -> set:
    """
    Return a version of base union with the words mentioned in add and minus
    those mentioned in remove.
    """
    
    new = base.copy()
    new -= set(remove.split())
    new |= set(add.split())
    return new

# We don't strip apostrophes, nor use nltk tokenize, so manual contractions
contractions = ("don't won't can't wouldn't shouldn't couldn't doesn't didn't"
                " hasn't haven't isn't aren't wasn't weren't i'm you're he's"
                " she's it's we've they've who's who've i'd you'd he'd she'd"
                " it'd we'd they'd who'd")

_BASE = _modify_base(_BASE, contractions, 's t don')

# Stopwords for synonymization
okay_syns = ('until before again very just')
poor_syns = ('cat january february march april may june july august'
             ' september october november december time')

SYN = _modify_base(_BASE, okay_syns, poor_syns)

# Stopwords for rhyming
okay_rhyme = ('through between below under over other why while now above same'
              ' until further down me you i')

RHYME = _modify_base(_BASE, okay_rhyme)

# Stopwords for ellipsis
okay_ellipsis = ('or and just few both below there where while under myself'
                 ' yourself yourselves ourselves themself themselves herself'
                 ' himself itself why what how many much before against down'
                 ' further over as me you i')

ELLIPSIS = _modify_base(_BASE, okay_ellipsis)

#===============================================================================
# CLEAN UP EXTRA
#===============================================================================

del stopwords, _BASE, _modify_base
del contractions, okay_syns, poor_syns, okay_rhyme, okay_ellipsis
