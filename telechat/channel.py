# ----------------------------------------------------------------------------
# channel.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from types import *

# Change these depnding on how you subclass TCChannel in the factory
CHANNEL_DEFAULT = 1
CHANNEL_VALID_MSG = "Channel must be a number from 1 to 99."

# ----------------------------------------------------------------------------

class TCChannel:
    # UNIQUE identifier.
    name        = None
    # Description, or none for untitled
    title       = None
    # Allow users to join this channel
    locked      = False
    # Do not destruct channel when last user leaves
    persist     = False
    # Initilize this to [] in your __init__
    users       = None
    
    @staticmethod
    def nameTransform(name):
        """Try to keep the rest of the code as channel-name agnostic as
        possible, in case we want to switch to string-based channel names
        or something like that in the future."""
        pass

    def nameToStr(self):
        """More abstract name/type goodness."""
        return str(self.name)

# ----------------------------------------------------------------------------
# TODO special channels 91-99 that only hold 90-x users

class TCNumberedChannel(TCChannel):
    """The Classic Telechat channel naming scheme (integers 1-99)"""

    def __init__(self,  name):
        assert type(name) is IntType
        if name < 1 or name > 99:
            raise Exception(CHANNEL_VALID_MSG)
        self.name = name
        self.users = []
    
    def __str__(self):
        return "%s: {%s}" % (self.nameToStr(), ','.join(map(str, self.users)))
    
    @staticmethod
    def nameTransform(name):
        return int(name)
        
    def nameToStr(self):
        return "%02d" % self.name
