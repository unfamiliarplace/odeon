#===============================================================================
# CONTROLLER
# Runs the program: prompts the user for text and options and generates poems.
#
# EXPORTS
# run
#===============================================================================

from manipulation.manipulator import Manipulator
from language.poem import Poem
from controller._logger import Logger
from controller._option import OptionODict, OptionODict

from resources import prondict, syndict, corpora
import nltk
import options as o

import os
from collections import OrderedDict as ODict

# Globally available demos; overwritten in run if run is passed any demos
DEMOS = {}

#===============================================================================
# LOAD OPTIONS
#===============================================================================

def _split_prompt(prompt: str) -> str:
    """Return a version of prompt split neatly at 80 chars."""
    
    pieces = []
    
    # Initial split at ? (and restore ?)
    pre_q, post_q = prompt.split('?')    
    pieces.append(pre_q + '?')
    
    # While longer than is nice to read, split at the closest bar to halfway
    while len(post_q) > 72 and '|' in post_q:
        i_half = len(post_q) // 2
        i_bar = post_q.find('|', i_half)
        pre, post_q = post_q[:i_bar], post_q[i_bar + 1:]
        pieces.append(pre)
    
    # Append the last piece and join with newlines
    pieces.append(post_q)
    return '\n'.join([piece.strip() for piece in pieces]) + ' '


def _prompt_option(option: OptionODict) -> object:
    """Prompt the user to select among the choices for the given option."""
    
    prompt = option.format_prompt()
    prompt = _split_prompt(prompt)
    
    # Prompt until valid input
    choice = input(prompt).lower().strip()
    while not option.check_choice(choice):
        print('Sorry, that was not one of the options.')
        choice = input(prompt).lower().strip()
    
    # Identify the value indicated by the prompt string
    return option.interpret_choice(choice)


def _process_option(option: OptionODict, options_dict: dict) -> object:
    """
    Check if the given option meets its dependencies. If so, prompt and set.
    If not, set it to its default value.
    """
    
    # Set the option alias for the eval string
    exec('{} = {}'.format(option.OPTIONS_ALIAS, options_dict))
    
    # Evaluate dependencies
    if not option.deps or eval(option.deps):
        return _prompt_option(option)
    
    # Set to default value otherwise
    else:
        return option.default
    
        
def _load_options(option_table: tuple, options_dict: dict) -> dict:
    """ Load the given table of options."""
    
    for option in option_table:
        
        # If option is not a blank, process it
        if option:
            options_dict[option.name] = _process_option(option, options_dict)
            
        # Otherwise print a blank line
        else:
            print()
            
#===============================================================================
# RESOURCES
#===============================================================================

def _load_resources() -> None:
    """
    Load all resources that are required by the options.
    For speed, they will only be loaded once; repeated calls will not reload.
    """
    
    # If meter or rhyme will be used
    if o.OPTIONS['M'] or o.OPTIONS['R']:
        
        # Load the pronunciation dictionary
        if not o.PROND:
            o.LOG.event('Loading pronunciation dictionary...')
            o.PROND = prondict.load_prond()
    
    # If synonymization will be used
    if o.OPTIONS['S']:
        
        # Load the synonym dictionary
        if not o.SYND:
            o.LOG.event('Loading synonym dictionary...')
            o.SYND = syndict.load_synd()
        
        # Load poetry corpus and create frequency distribution
        if not (o.C_POEMS and o.FD_POEMS):
            o.LOG.event('Loading poetry corpus...')
            o.C_POEMS = corpora.load_poetry_corpus(o.OPTIONS['C_PO'])
            o.FD_POEMS = nltk.FreqDist(w.lower() for w in o.C_POEMS.words())
        
        # Load prose corpus and create frequency distribution
        if not (o.C_PROSE and o.FD_PROSE):
            o.LOG.event('Loading prose corpus...')
            o.C_PROSE = corpora.load_prose_corpus(o.OPTIONS['C_PR'])
            o.FD_PROSE = nltk.FreqDist(w.lower() for w in o.C_PROSE.words())

#===============================================================================
# SELECT TEXT
#===============================================================================

TS_OPTIONS, TS_DEMO, TS_TEXT, TS_FILE = {}, 'demo', 'text', 'file'
DEMO_OPTIONS, DEMO_DEFAULT = {}, 'This is a poem. You, too, go home.'

def _select_text_source():
    """Get the text source selection and store it in TS_OPTIONS."""
    
    values = [('Text', TS_TEXT), ('File', TS_FILE)]
    
    if DEMOS: values.insert(0, ('Demo', TS_DEMO))
        
    option = OptionODict('SOURCE', TS_TEXT, 'What will your source be',
                         odict=ODict(values))
    
    _load_options([option], TS_OPTIONS)
    
    
def _select_demo():
    """Have the user select a demo."""
    
    option = OptionODict('DEMO', DEMO_DEFAULT, 'Which demo', odict=DEMOS)    
    _load_options([option], DEMO_OPTIONS)
    
    
def _select_filename() -> str:
    """Return the filename the user selects."""
    
    print('Current working directory, for reference: {}'.format(os.getcwd()))
    
    filename = input('Enter filename: ')
    while not os.path.exists(filename):
        print('Could not find that file.')
        filename = input('Enter filename: ')
        
    return filename


def _read_text_file(filename: str) -> str:
    """Return the contents of the file specified by the given filename."""
    
    with open(filename, 'r') as f:
        return f.read().replace('\n', ' ')
    
    
def _text_from_demo() -> str:
    """Return the text from the demo the user selects."""
    
    _select_demo()
    return DEMO_OPTIONS['DEMO']


def _text_from_input() -> str:
    """Return the text the user manually enters."""
    
    return input('Your text: ')


def _text_from_file() -> str:
    """Return the text in the file the user specifies."""
    
    filename = _select_filename()
    return _read_text_file(filename)


def _get_text(**text_args) -> str:
    """Return the text from the source the user selects."""
    
    # First see whether the user selected it at the command line.
    
    if text_args['demo_mode']:
        return _text_from_demo()
    
    elif text_args['text']:
        return text_args['text']
    
    elif text_args['fname']:
        return _read_text_file(text_args['fname'])
    
    # Otherwise, have them select it now.
    
    _select_text_source()
    src = TS_OPTIONS['SOURCE']
    
    if src is TS_DEMO:
        return _text_from_demo()
    
    elif src is TS_TEXT:
        return _text_from_input()
    
    elif src is TS_FILE:
        return _text_from_file()
    
#===============================================================================
# SELECT OPTIONS
#===============================================================================

OC_OPTIONS, OC_PRE, OC_MOD, OC_CUS = {}, 'preset', 'modify', 'custom'
PRESET_OPTIONS, PRESET_DEFAULT = {}, o.PRESETS[0]

def _select_options_config():
    """Get the options type selection and store it in OT_OPTIONS."""
    
    values = [('Preset', OC_PRE),
              # ('Modify preset', OC_MOD),
              ('Custom', OC_CUS)]
    
    option = OptionODict('CONFIG', OC_PRE, 'How will you configure options',
                         odict=ODict(values))
    
    _load_options([option], OC_OPTIONS)
    

def _select_preset():
    """Have the user select a preset."""
    
    values = [(preset.name, preset) for preset in o.PRESETS]
    option = OptionODict('PRESET', PRESET_DEFAULT, 'Which preset',
                         odict=ODict(values))
    
    _load_options([option], PRESET_OPTIONS)
    

def _load_preset(preset: dict, options_dict: dict):
    """Load the given preset into the options."""
    
    for k, v in preset.config.items():
        options_dict[k] = v
        
        
def _options_from_preset():
    """Load the options from the preset the user selects."""
    
    _select_preset()
    _load_preset(PRESET_OPTIONS['PRESET'], o.OPTIONS)
    

#TODO: Implement
def _options_from_modify_preset():
    """Load the options as modified in the preset the user selects."""
    
    #===========================================================================
    # _select_preset()
    # load_preset(PRESET_OPTIONS['PRESET'], o.OPTIONS)
    #===========================================================================
    pass

def _options_from_custom():
    """Load the custom options the user selects."""
    
    _load_options(o.O_TABLE, o.OPTIONS)


def _get_options():
    """Load the options from the configuration the user selects."""
    
    _select_options_config()
    config = OC_OPTIONS['CONFIG']
    
    if config is OC_CUS:
        _options_from_custom()
        
    elif config is OC_PRE:
        _options_from_preset()
        
    elif config is OC_MOD:
        _options_from_modify_preset()        
        
#===============================================================================
# FORMAT POEMS
#===============================================================================

def _format_poem(poem: Poem, score: tuple) -> str:
    """
    Return a formatted string of the poem and its score vectors.
    The score tuple is of the form (score, Vectors).
    """
    
    intro = ''
    
    for vector in score[1]:
        intro += '\n{}'.format(vector)
        
    return '{}\n\n{}'.format(intro, poem)


def _print_poems(poems: list):
    """Print each poem with its score and a prompt to show the next one."""
    
    for i, (poem, score) in enumerate(poems):
        print(_format_poem(poem, score))
        
        if i < len(poems) - 1:
            cont = input('\nPress Enter to see the next poem or "q" to quit. ')
            
            if cont.lower() == 'q':
                break

#===============================================================================
# MAIN PROGRAM
#===============================================================================

def run(demos: dict={}, **text_args):
    """Get the user's text and options and run the manipulator."""
    
    o.LOG = Logger()
    
    global DEMOS
    DEMOS = demos
    
    text = _get_text(**text_args)
    o.LOG.event('Text chosen.')
    print()
    
    _get_options()
    print()
    o.LOG.event('Options saved.')
    print()
    
    o.LOG.event('Loading resources...')
    _load_resources()  
    print()
    
    o.LOG.event('Processing text...')
    m = Manipulator(text)
    
    o.LOG.event('Generating poems...')
    m.manipulate()
    
    poems = list(m.get_poems()) # Each is of the form (Poem, (score, Vectors))
    
    if poems:
    
        o.LOG.event('Scoring poems...')
        
        # Each is of the form (Poem, (score, Vectors))
        poems = sorted(poems, key=lambda p_s: p_s[1][0], reverse=True)
        print()
    
        o.LOG.event('Ready.')
        print()
        
        input('Press Enter to see the first poem.')
        _print_poems(poems)
        print()
        
        print('Finished.')
        
    else:
        o.LOG.event('No poems could be generated.')
