# ----------------------------------------------------------------------------
# protocol.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from time import sleep
from random import random
from twisted.conch import telnet
from telechat.user import TCUser
from telechat.channel import TCChannel
from telechat.config import TCConfig
import telechat.const

LOGIN_HEADER = """
These special user names can be used without logging on:
   "n" or "new" to register as a new user,
   "w" or "who" to see who is currently online,
   "r" or "recent" to see who has been online recently,
   "q" or "quit" to close connection immediately.
"""

# ----------------------------------------------------------------------------

class TCSimpleProtocol(telnet.StatefulTelnetProtocol):
    """The 'classic' Telechat interface protocol. If client is typing, buffers
    output until newline is detected.  Responsible for:
    
    - Negotiating telnet options (character-at-a-time)
    - Buffering & validating input
    - Input state machine
    - Parsing commands
    - Writing output to transport
    - Displaying prompts
    
    Telnet option negotation mostly ripped off from
    twist.conch.telnet.TelnetBootstrapProtocol
    """
    
    channel     = None
    user        = None
    _inbuf      = ''
    _outbuf     = ''
    
    # ----------------------------------------------------

    def __init__(self, username):
        self.user = TCUser(username)
        # TODO factory lookup from username.channel
        self.channel = TCChannel()

    # ----------------------------------------------------

    def enableRemote(self, option):
        if option == telnet.ECHO:
            return True
        elif option == telnet.SGA:
            return True
        print "enableRemote rejected TELOPT %r" % (option)
        return False

    def disableRemote(self, option):
        print "disableRemote rejected TELOPT %r" % (option)

    def enableLocal(self, option):
        if option == telnet.ECHO:
            return True
        elif option == telnet.SGA:
            return True
        print "enableLocal rejected TELOPT %r" % (option)
        return False

    def disableLocal(self, option):
        if option == telnet.ECHO:
            return True
        print "disableLocal rejected TELOPT %r" % (option)

    # ----------------------------------------------------

    def connectionMade(self):
        print "New authenticated connection from", self.transport.getPeer().host
        if not self.transport.factory.isConnectionAllowed(self):
            self.writeLine("Too many connections, try later") 
            self.transport.loseConnection()
            return
        for opt in (telnet.SGA, telnet.ECHO):
            self.transport.will(opt)
        self.state = 'PostLogin'
        self.lineReceived(None) # trigger state change

    def connectionLost(self, reason):
        print "Lost connection from", self.transport.getPeer().host
        if self.state not in ('User', 'Password'):
            self.transport.factory.removeClient(self)
        telnet.StatefulTelnetProtocol.connectionLost(self, reason)
        
    # ----------------------------------------------------

    def telnet_PostLogin(self, data):
        self.transport.write("\r\n")
        self.transport.write(TCConfig().postlogin_msg)
        self.transport.factory.addClient(self)
        return 'Idle'

    def telnet_Idle(self, data):
        #print "Idle recv", repr(data)
        eol = False
        for ch in data:
            eol = self.charReceived(ch)
        if not eol:
            return 'Typing'
            
    def telnet_Typing(self, data):
        #print "Typing recv", repr(data)
        eol = False
        for ch in data:
            eol = self.charReceived(ch)
        if eol:
            self.flushOutbuf()
            return 'Idle'

    def dataReceived(self, data):
        # StatefulTelnetProtocol is line-oriented, so fake it here
        self.lineReceived(data)

    def charReceived(self, ch):
        # TODO flood protection
        # TODO abstract receiver class - regular typing, commands, etc
        if ch == '\r' or ch == '\n':
            if len(self._inbuf) > 0:
                self.transport.write("\r\n")
                self.transport.factory.lineReceived(self, self._inbuf);
                self._inbuf = ''
            return True
        self._inbuf += ch
        self.transport.write(ch)
        return False
            
    def flushOutbuf(self):
        # Does NOT check self.state, use with caution.
        if len(self._outbuf) > 0:
            self.transport.write(self._outbuf)
            self._outbuf = ''
            
    def writeLine(self, line):
        if self.state in ('Idle', 'PostLogin'):
            self.transport.write(line + "\r\n")
        else:
            # TODO outbut max size/truncation
            self._outbuf += line + "\r\n"


# ----------------------------------------------------------------------------

class TSAuthenticatingTelnetProtocol(telnet.AuthenticatingTelnetProtocol):
    
    def connectionMade(self):
        print "New connection from", self.transport.getPeer().host, "starting login"
        # TODO print version and NOTICE
        self.transport.write('\r\n' + telechat.const.WELCOME_HEADER + '\r\n')
        self.transport.write(TCConfig().prelogin_msg)
        self.transport.write(LOGIN_HEADER + '\r\n')
        telnet.AuthenticatingTelnetProtocol.connectionMade(self)
        
    def telnet_User(self, line):
        special = False
        if line == 'who' or line == 'w':
            # TODO
            special = True
        elif line == 'quit' or line == 'q':
            self.transport.write('bye!\r\n')
            self.transport.loseConnection()
            special = True
            return 'Discard'
        elif line == 'new' or line == 'n':
            # TODO
            special = True
        elif line == 'recent' or line == 'r':
            # TODO
            special = True
        if special:
            print "Caught special username", line
            telnet.AuthenticatingTelnetProtocol.connectionMade(self)
            return 'User'
        else:
            return telnet.AuthenticatingTelnetProtocol.telnet_User(self, line)
    
    def _ebLogin(self, failure):
        print "Failed auth from", self.transport.getPeer().host
        print failure
        sleep(random() * 2.0)
        telnet.AuthenticatingTelnetProtocol._ebLogin(self, failure)

