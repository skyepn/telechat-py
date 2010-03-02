# ----------------------------------------------------------------------------
# factory.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import TelnetTransport
from telechat.protocol import TSAuthenticatingTelnetProtocol

MAX_CLIENTS = 512

# ----------------------------------------------------------------------------

class TelechatFactory(ServerFactory):
    """Stateful Telechat code goes here.  Responsible for:
    
    - Managing the list of connections aka protocols/clients/users
    - Managing the list of channels
    - Distributing output
    """
    
    protocol    = None
    _portal     = None
    _clients    = []
    
    def __init__(self, portal):
        self._portal = portal
        self.protocol = lambda:TelnetTransport(TSAuthenticatingTelnetProtocol, self._portal)
    
    def isConnectionAllowed(self, client):
        if len(self._clients) > MAX_CLIENTS:
            print "Reached max clients %d, rejecting connection from %s" % (MAX_CLIENTS, client.transport.getPeer().host)
            return False
        return True
    
    def addClient(self, client):
        self._clients.append(client)
        self.writeLineAll("-- Logged on channel %02d: %s/%s" % 
                (client.channel.number, client.user.username, client.user.nickname))
        return True
        
    def removeClient(self, client):
        self._clients.remove(client)
        self.writeLineAll("-- DISCOnnected! channel %02d: %s/%s" % 
                (client.channel.number, client.user.username, client.user.nickname))
        return True
    
    def lineReceived(self, client, line):
        # TODO channel
        self.writeLineAll("%s/%s: %s" % (client.user.username, client.user.nickname, line))
        
    def writeLineAll(self, line):
        for c in self._clients:
            c.writeLine(line)
