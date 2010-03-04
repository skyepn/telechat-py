# ----------------------------------------------------------------------------
# input.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.
#
# These classes are fed characters by the Protocol instances and handle
# parsing the input.  If a command is detected, for instance, a talking
# class will hand off the buffer to a command class, which will prompt,
# validate the command, and dispatch as necessary.

from telechat import command
from telechat import utils

# Max length for any single input line
INPUT_MAXLEN = 512 # TODO

# ----------------------------------------------------------------------------

class TCInputHandlerFactory:
    
    def __init__(self, client):
        self.client = client
        
    def factory(self, ch):
        """Choose a factory based on the first character of the input."""
        assert len(ch) == 1
        if ch == '\r' or ch == '\n':
            return None
        elif ch == command.COMMAND_CHAR:
            return TCCommandInputHandler(self.client, None)
        else:
            return TCLineInputHandler(self.client, None)

# ----------------------------------------------------------------------------

class TCInputHandler:
    
    def __init__(self, client, buffer):
        self._client    = client
        self._inbuf     = buffer or ''
        self._complete  = False
    
    def process(self, ch):
        """Add a character from the input stream to this handler.
        Returns a string to echo back to the user.
        """
        return ch
    
    def isComplete(self):
        """Should return True if the handler has finished processing input.
        This is checked after every addChar to see if the user can return 
        to the Idle state."""
        return self._complete

# ----------------------------------------------------------------------------

class TCLineInputHandler(TCInputHandler):
    
    def empty(self):
        return len(self._inbuf) == 0
        
    def process(self, ch):
        assert not self._complete
        if ch == '\r' or ch == '\n':
            # Ignore CRLF on a blank line
            if self.empty():
                return ''
            self._complete = True
            self._client.transport.factory.lineReceived(self._client, self._inbuf);
            return '\r\n'
        else:
            self._inbuf += ch
            return ch
    

# ----------------------------------------------------------------------------

class TCCommandInputHandler(TCInputHandler):
    state       = None
    _command    = None
    _promptnum  = 0
    
    def process(self, ch):
        assert not self._complete
        echo = ch
        if self.state is None:
            assert ch == command.COMMAND_CHAR
            self.state = 'Command'
        elif self.state == 'Command':
            cmdtuple = command.TCCommand.findByChar(ch)
            echo += " -> "
            #print "got cmdtuple for", ch, cmdtuple
            if cmdtuple is None:
                echo += "Invalid command, type " + command.COMMAND_CHAR + command.COMMAND_HELP_CHAR + " for help.\r\n"
                self._complete = True
            else:
                echo += self.dispatchCommand(cmdtuple)
        elif self.state == 'Prompt':
            if self._prompt.echo != command.PROMPT_ECHO:
                echo = ''
            if self._prompt.mode == command.PROMPT_MODE_CHAR:
                echo += "\r\n" + self.dispatchPrompt(ch)
            elif self._prompt.mode == command.PROMPT_MODE_LINE:
                # buffer the line until CRLF
                if ch == '\r' or ch == '\n':
                    echo += "\r\n" + self.dispatchPrompt(self._inbuf)
                else:
                    self._inbuf += ch
            else:
                raise TypeError("bad prompt mode " + self._prompt.mode)
        else:
            raise TypeError("bad command state " + self.state)
        return echo
        
    def dispatchCommand(self, cmdtuple):
        assert len(cmdtuple) == 5
        cmdclass = command.TCCommand.buildClassName(cmdtuple)
        try:
            exec "self._command = command.%s(cmdtuple, self._client)" % (cmdclass,)
        except:
            self._complete = True
            return "ERROR: Not implemented. Please contact the sysop with details.\r\n"
        #utils.dumpObj(self._command)
        return "(" + self._command.shortname + ") " + self._command.description + "\r\n" + self.displayPrompt()

    def displayPrompt(self):
        if self._promptnum >= self._command.countPrompts():
            # No prompts, or all prompts completed. Checks every time just in
            # case the prompts for this command are dynamic.
            echo = self._command.execute() or ''
            self._complete = True
        else:
            self._prompt = command.TCPrompt(self._command.getPrompt(self._promptnum))
            echo = self._prompt.prompt
            self.state = 'Prompt'
        return echo
        
    def dispatchPrompt(self, data):
        exec "echo = self._command.prompt_" + self._prompt.name + "(data) or ''"
        self._promptnum += 1
        self._inbuf = ''
        echo += self.displayPrompt() or ''
        return echo


