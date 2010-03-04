# ----------------------------------------------------------------------------
# command.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

import time
import random
from telechat.user import *
import telechat.channel

COMMAND_CHAR        = '/'
COMMAND_HELP_CHAR   = '?'
COMMAND_MAP         = (
#   char    shortname       category    min level           description
	('?',   'help',         'basic',    USER_LEVEL_NEW,     'Show list of commands'),
	('a',   'who',          'basic',    USER_LEVEL_NEW,     'Show who is logged in'),
	('-',   'recent',       'basic',    USER_LEVEL_NEW,     'List recent users'),
	('n',   'nick',         'basic',    USER_LEVEL_NEW,     'Change nickname'),
	('p',   'msg',          'basic',    USER_LEVEL_REGULAR, 'Send private message to a user'),
	(',',   'reply',        'basic',    USER_LEVEL_NEW,     'Reply to private message'),
	('/',   'again',        'basic',    USER_LEVEL_REGULAR, 'Send one more private message'),
	('i',   'info',         'basic',    USER_LEVEL_REGULAR, 'Inquire about a user'),
	('d',   'broadcast',    'basic',    USER_LEVEL_NEW,     'Broadcast message to everyone'),
	('e',   'typing',       'basic',    USER_LEVEL_NEW,     'Check for other users typing'),
	('q',   'quit',         'basic',    USER_LEVEL_NEW,     'Log off from the chat'),

	('w',   'emote',        'fun',      USER_LEVEL_NEW,     'Emote some action'),
	('H',   'hug',          'fun',      USER_LEVEL_REGULAR, 'Hug another user'),
	('S',   'smooch',       'fun',      USER_LEVEL_REGULAR, 'Smooch another user'),
	('b',   'beep',         'fun',      USER_LEVEL_REGULAR, 'Send a beep to another user'),

	('m',   'offread',      'mail',     USER_LEVEL_REGULAR, 'Read offline messages'),
	('M',   'offmsg',       'mail',     USER_LEVEL_REGULAR, 'Send private offline message'),

	('x',   'squelch',      'privacy',  USER_LEVEL_NEW,     'Squelch another user'),
	('r',   'rsquelch',     'privacy',  USER_LEVEL_NEW,     'Reverse squelch'),

	('c',   'chan',         'channel',  USER_LEVEL_REGULAR, 'Change channel'),
	('C',   'chwho',        'channel',  USER_LEVEL_NEW,     'List users on channel'),
	('E',   'chtyping',     'channel',  USER_LEVEL_NEW,     'Check users typing on channel'),
	('N',   'chname',       'channel',  USER_LEVEL_REGULAR, 'Name current channel'),
	('U',   'chunname',     'channel',  USER_LEVEL_REGULAR, 'Un-name current channel'),

	('V',   'verify',       'misc',     USER_LEVEL_NEW,     'Verify your email address'),
	('t',   'time',         'misc',     USER_LEVEL_NEW,     'Display current time'),
	('l',   'clear',        'misc',     USER_LEVEL_NEW,     'Clear screen'),
	('V',   'version',      'misc',     USER_LEVEL_NEW,     'Print server version info'),
	('1',   'prelogin',     'misc',     USER_LEVEL_NEW,     'Read pre-login message'),
	('2',   'postlogin',    'misc',     USER_LEVEL_NEW,     'Read post-login message'),

	('&',   'setpassword',  'options',  USER_LEVEL_NEW,     'Change password'),
	('F',   'togemailvis',  'options',  USER_LEVEL_NEW,     'Toggle email visibility'),
	('3',   'setwidth',     'options',  USER_LEVEL_NEW,     'Set screen width'),
	('#',   'togcolor',     'options',  USER_LEVEL_NEW,     'Toggle colorization mode'),
	('g',   'setcolor',     'options',  USER_LEVEL_NEW,     'Select color of your messages'),
	('4',   'togbroadcast', 'options',  USER_LEVEL_REGULAR, 'Toggle broadcast visibility'),
	('6',   'togbeep',      'options',  USER_LEVEL_REGULAR, 'Toggle beeping mode'),
	('*',   'setformat',    'options',  USER_LEVEL_REGULAR, 'Change message & list format'),
#	('j',   'tognl',        'options',  USER_LEVEL_REGULAR, 'Toggle newlines mode'),
#	('u',   'setnl',        'options',  USER_LEVEL_NEW,     'Change newline character'),
	('T',   'settz',        'options',  USER_LEVEL_NEW,     'Set your time zone'),
	
	('k',   'kick',         'sysop',    USER_LEVEL_POWER,   'Kick a user off the chat'),
	('=',   'op',           'sysop',    USER_LEVEL_ADMIN,   'Enter Operator interface'),
	('z',   'pa',           'sysop',    USER_LEVEL_ADMIN,   'Broadcast PA message'),
)

# ----------------------------------------------------------------------------

class TCCommand:
    """Command base class.  Every command should subclass this in the form
    TCCommand_shortname.  If the command prompts for data, then override and
    fill the _prompts var (or add a predefined Mixin class) with an ordered
    tuple of (name, buffering, echo, prompt).  The tuple will be itereated
    over with command.prompt_name called for the input for each.  Finally,
    command.execute() will be called."""
    
    _prompts = ()
    
    def __init__(self, cmdtuple, client):
        (self.char, self.shortname, self.category, self.permission, self.description) = cmdtuple
        self._client = client
        
    @staticmethod
    def findByChar(ch):
        assert len(ch) == 1
        for command in COMMAND_MAP:
            if command[0] == ch:
                return command
        return None
        
    @staticmethod
    def buildClassName(cmdtuple):
        return "TCCommand_" + cmdtuple[1]
    
    def execute(self):
        """Run the command. Return any string you want echoed to the client."""
        pass
        
    def countPrompts(self):
        return len(self._prompts)
        
    def getPrompt(self, ix):
        return self._prompts[ix]

    def prompt_string(self, data):
        self._string = data.strip()

# ----------------------------------------------------------------------------

PROMPT_MODE_CHAR = 0
PROMPT_MODE_LINE = 1

PROMPT_NOECHO = 0
PROMPT_ECHO = 1

class TCPrompt:
    def __init__(self, tuple):
        (self.name, self.mode, self.echo, self.prompt) = tuple

class TCPromptConfirmMixin:
    """To use this, subclass BEFORE TCCommand, so our prompts get used."""
    _prompts = (
        ('confirm', PROMPT_MODE_CHAR, PROMPT_ECHO, "Are you sure? [y/n] "),
    )
    _confirmed = False
    
    def prompt_confirm(self, data):
        print "prompt_confirm got", data
        if data == 'y' or data == 'Y':
            self._confirmed = True

# ----------------------------------------------------------------------------
# The Commands
# ----------------------------------------------------------------------------

class TCCommand_emote(TCCommand):
    _prompts = (
        ('string', PROMPT_MODE_LINE, PROMPT_ECHO, "Action: "),
    )
    
    def execute(self):
        if not self._string:
            return
        self._client.factory.writeLineChannel(
                self._client, self._client.channel,
                "** %s %s **" % (self._client.user.id, self._string))
                
# ----------------------------------------------------------------------------

class TCCommand_quit(TCPromptConfirmMixin, TCCommand):
    
    def execute(self):
        if not self._confirmed:
            return
        # TODO update db ts_last_logout
        self._client.user.cleanQuit = True
        self._client.transport.loseConnection()
        return "Goodbye!\r\n"

# ----------------------------------------------------------------------------

class TCCommand_time(TCCommand):    
    
    def execute(self):
        # TODO compute local and server time based on tz
        # TODO time on
        return "System Time: " + time.ctime() + "\r\n"

# ----------------------------------------------------------------------------

class TCCommand_chan(TCCommand):
    _prompts = (
        ('string', PROMPT_MODE_LINE, PROMPT_ECHO, "Channel: "),
    )
    
    def execute(self):
        if not self._string:
            return
        try:
            chan = self._client.factory.joinChannel(self._client, self._string)
        except ValueError:
            return telechat.channel.CHANNEL_VALID_MSG + "\r\n"
        except Exception, e:
            return str(e) + "\r\n"
        self._client.factory.leaveChannel(self._client, self._client.channel)
        self._client.channel = chan
        return "Channel changed to %s.\r\n" % (chan.nameToStr(),)
        
# ----------------------------------------------------------------------------

class TCCommand_who(TCCommand):
    
    def execute(self):
        outbuf = str()
        anonlist = list()
        for chan in self._client.factory.getChannels():
            if chan.title is not None:
                outbuf += "Channel %s -- %s\r\n" % (chan.nameToStr(), chan.title)
            if not len(chan.users):
                outbuf += "\tempty\r\n"
            else:
                for user in chan.users:
                    if chan.title is not None:
                        outbuf += "\t" + self._client.user.formatWho(user) + "\r\n"
                    else:
                        # Show everything to admins
                        if self._client.user.level >= USER_LEVEL_POWER:
                            showchan = chan.nameToStr() + ": "
                        else:
                            showchan = str()
                        anonlist.append("\t" + showchan + self._client.user.formatWho(user) + "\r\n")
        if len(anonlist):
            outbuf += "All other channels are unnamed or unused\r\n" 
            if self._client.user.level >= USER_LEVEL_POWER:
                outbuf += "(But I'll show you the channel numbers anyway)\r\n"
            else:
                random.shuffle(anonlist) # Randomize order for anonymity
            outbuf += ''.join(anonlist)
        return outbuf
        
# ----------------------------------------------------------------------------
