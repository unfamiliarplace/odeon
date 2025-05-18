#===============================================================================
# LOGGER
# Keeps track of events with their timestamps.
#
# EXPORTS
# Logger, Logger.event, Logger.get_events
#===============================================================================

import time

class Logger:
    """Prints events and stores them with their timestamps."""

    def __init__(self):
        """Initializes this Logger with an empty list of events."""  
              
        self._events = []
        
        
    def event(self, text: str):
        """Print the text of the event and store it as a (time, text) tuple."""    
            
        print(text)
        self._events.append((time.time, text))
           
        
    def get_events(self) -> list:
        """Return the (time, text) event tuples from this Logger."""
           
        return self._events
    