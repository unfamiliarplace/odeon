#===============================================================================
# ODEON
# The prose to poetry converter.
# v 0.2
# April 10, 2016
#===============================================================================

#==============================================================================
# FUTURE
# 
# -- indentation
# -- stanza
# -- modify existing preset; load options at cmd line; load options from file
# -- break lines using syntax tree with pos tagging
# -- score alliteration, assonance, internal rhyme, meter scheme
# -- statistical poeticness: train and pickle a classifier using the corpora,
#        then use it to measure words instead of having to load corpora
# -- more sophisticated meter, particularly detection of stressed/unstressed,
#        e.g. pos tagging to determine if 'through' is prep. (US) or adv. (SS)
# -- even better rhyme schem matching, e.g. so 'ABCB' matches '.A'. This can
#        be done by also symbolizing in reverse.
# -- allow multiple texts per run (save on load time!)
# -- option to rearrange lines after they have been determined
#
# VERY LONG-TERM FUTURE
#
# A web app with an interface to a Python implementation. The interface will
# give users the ability to pick a text and options much more easily, and
# present poems in a carousel along with various stats. Users can upvote and
# downvote poems, which will privilege certain configurations in tandem with
# the current scoring system. Users can log in and save and share poems.
#==============================================================================

import sys, getopt, os

from controller import controller
from collections import OrderedDict as ODict

#===============================================================================
# Some temporary demos
#===============================================================================

DEMOS = ODict([
               ('Madman', 'I am a mad man who lives in a bad desert pan'),
               ('Hairfuzz', 'There was a bat whose hair fuzz was flat when he does that'),
               ('Catbat', 'There was a cat who ate a bat but mate that was the end of the mat is that not great for you'),
               ('Walkblock', 'In a land far far away there lived a fellow by the name of Jake and he loved to take the odd walk around the block'),
               ('Butterscotch', 'I had a cat, once, named Butterscotch. He died in April. It was a long time ago, I know, but all the same, I miss him. I repeat his name daily. He was the finest cat I had ever seen.'),
               ('Thingstuff', 'The thing was cool. What did you think of that? The stuff I did there?'),
               ('Yogamat', 'North. I am a cat who knows where it is at. And though that is great, some people will buy a yoga mat. Retaliate.'),
               ('Provedeaf', "His friends demanded he get retested to prove that he was deaf. The doctors played recordings of dogs barking, car doors slamming, truck-reversing beeps. The man did not react, but he had always been a convincing actor, so in the growing phenomenon of his musical ability his friends scheduled an fMRI to see if the activity of his audio cortex demonstrated that he could hear."),
               ('ButterscotchYear', 'I had a cat, once, named Butterscotch. He died in April 2013. It was a long time ago, I know, but all the same, I miss him. I repeat his name daily. He was the finest cat I had ever seen.'),
])

#===============================================================================
# Parse options
#===============================================================================

SHORTOPTS = 'hdt:f:'
LONGOPTS = ['help', 'demo', 'text=','file=']
USAGE = 'Odeon OR Odeon --demo OR Odeon --text "<text>" OR Odeon --file <file>'

def _get_opts(argv) -> dict:
    """
    Return a kwargs-style dictionary of the supplied arguments:
    
    --demo_mode (bool)
    --text (str)
    --fname (str)
    
    Exit if more than one is supplied. They are incompatible.
    """

    text_args = {'demo_mode': None, 'text': None, 'fname': None}
    
    try:
        opts, _ = getopt.getopt(argv, SHORTOPTS, LONGOPTS)
        
    except getopt.GetoptError:
        print(USAGE)
        sys.exit(2) 
    
    else:
        for opt, arg in opts:
            
            # Help
            if opt in ('-h', '--help'):
                print(USAGE)
                sys.exit()
                
            # Demo mode
            elif opt in ('-d', '--demo'):
                text_args['demo_mode'] = True
                
            # Text
            elif opt in ('-t', '--text'):
                text_args['text'] = arg
                
            # File
            elif opt in ('-f', '--file'):
                
                if not os.path.exists(arg):
                    sys.exit("Could not find the file specified.")
                    
                else:
                    text_args['fname'] = arg
            
    if sum(bool(a) for a in text_args.values()) > 1:
        sys.exit('Supply either the demo mode flag, text, or filename,'
                 ' but not more than one.')
    
    return text_args

#===============================================================================
# Run
#===============================================================================

if __name__ == '__main__':
    
    # Grab options and run!
    text_args = _get_opts(sys.argv[1:])
    controller.run(DEMOS, **text_args)
