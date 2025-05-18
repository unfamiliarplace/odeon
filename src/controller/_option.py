#===============================================================================
# OPTION
# Represents options and presets in the program's configuration.
#
# EXPORTS
# Option, Option.format_prompt, Option.check_choice, Option.interpret_choice
# OptionBool, OptionStartInf, OptionRange, OptionODict
#===============================================================================

import re

#===============================================================================
# SEMI-ABSTRACT OPTION
#===============================================================================

class Option:
    """Data type for options."""
    
    OPTIONS_ALIAS = '_opts' # For dependencies to access during processing
    
    def __init__(self, *args, **kwargs):
        """
        Initialize this Option with the given name, default value, prompt,
        option type, dependencies, and values (if they need to be supplied).
        Translate the dependencies into evaluable expressions.
        """
        
        # Required parameters
        self.name, self.default, self.prompt = args
        
        # Translate dependencies
        self.deps = self._translate_dependencies(kwargs.get('deps', ''))
        

    def _translate_dependencies(self, deps: str='') -> str:
        """Return an evaluable string, translating option name placeholders."""
        
        return re.sub(r'__([\w_]+)__',
                      r'{}["\1"]'.format(self.OPTIONS_ALIAS),
                      deps)
        
        
    def format_prompt(self) -> str:
        """Return a formatted string of the prompt for this Option."""
        
        return '{}? {} : '.format(self.prompt, self._get_values_str())
    
    #===========================================================================
    # STUBS FOR SUBCLASSES
    #===========================================================================
    
    def _get_values_str(self) -> str:
        """Return a formatted string of the choices for this Option's value."""
       
        raise NotImplementedError()

    
    def check_choice(self, choice: str) -> bool:
        """Return True iff the given choice is valid for this Option."""
        
        raise NotImplementedError()
    
    
    def interpret_choice(self, ch: str) -> object:
        """Return the value intended by the given choice for this Option."""
        
        raise NotImplementedError()

#===============================================================================
# CONCRETE SUBCLASSES
#===============================================================================
    
class OptionBool(Option):
    """An Option with a boolean value."""       
    
    def _get_values_str(self):
        """Return a formatted string of the choices for this Option's value."""
        
        return ' 1: Yes | 2: No'
    
    
    def check_choice(self, ch: str) -> bool:
        """Return True iff the given choice is valid for this Option."""
        
        return ch in ('1', '2')
    
        
    def interpret_choice(self, ch: str) -> object:
        """Return the value intended by the given choice for this Option."""
        
        return ch == '1'
    

class OptionStartInf(Option):
    """An Option with an int value between a minimum and infinity."""    
    
    def __init__(self, *args, **kwargs):
        """Initialize as normal, plus save the minimum value."""
        
        super().__init__(*args, **kwargs)
        self.minimum = kwargs.get('minimum', 0)
        
    
    def _get_values_str(self):
        """Return a formatted string of the choices for this Option's value."""
        
        return ' Min. {} or "." for infinite'.format(self.minimum)
    
    
    def check_choice(self, ch: str) -> bool:
        """Return True iff the given choice is valid for this Option."""
        
        return ch == '.' or ch.isdigit() and int(ch) >= self.minimum
    
        
    def interpret_choice(self, ch: str) -> object:
        """Return the value intended by the given choice for this Option."""
        
        return int(ch) if ch.isdigit() else float('inf')
    

class OptionRange(Option):
    """An Option with an int value in an acceptable range."""    
    
    def __init__(self, *args, **kwargs):
        """Initialize as normal, plus save the range of allowed values."""
        
        super().__init__(*args, **kwargs)
        self.range = kwargs['range']
        
    
    def _get_values_str(self):
        """Return a formatted string of the choices for this Option's value."""
        
        return ' {} - {}'.format(min(self.range), max(self.range))
    
    
    def check_choice(self, ch: str) -> bool:
        """Return True iff the given choice is valid for this Option."""
        
        return ch.isdigit() and min(self.range) <= int(ch) <= max(self.range)
    
        
    def interpret_choice(self, ch: str) -> object:
        """Return the value intended by the given choice for this Option."""
        
        return int(ch)
    
    
class OptionODict(Option):
    """An option with an ordered dictionary of value names to data."""    
    
    def __init__(self, *args, **kwargs):
        """Initialize as normal, plus save the dictionary of allowed values."""
        
        super().__init__(*args, **kwargs)
        self.odict = kwargs['odict']
        
    
    def _get_values_str(self):
        """Return a formatted string of the choices for this Option's value."""
        
        values_str = ''        
        for i, value in enumerate(self.odict.keys()):
            values_str += '{:2}: {} |'.format(i + 1, value)            
        return values_str[:-2]
    
    
    def check_choice(self, ch: str) -> bool:
        """Return True iff the given choice is valid for this Option."""
        
        return ch.isdigit() and 1 <= int(ch) <= len(self.odict)
    
        
    def interpret_choice(self, ch: str) -> object:
        """Return the value intended by the given choice for this Option."""
        
        return list(self.odict.items())[int(ch) - 1][1]
    
#===============================================================================
# PRESET
#===============================================================================

class Preset:
    """Stores a preset name and a mapping of option names to values."""
    
    def __init__(self, name: str, config: dict):
        """Initialize this Preset with the given name and configuration."""
        
        self.name = name
        self.config = config
