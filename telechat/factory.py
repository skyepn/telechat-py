# ----------------------------------------------------------------------------
# factory.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import TelnetTransport
from telechat.protocol import TSAuthenticatingTelnetProtocol
from telechat.config import TCConfig

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
        # TODO check for duplicate user, kick off old (frozen) login
        self._clients.append(client)
        self.writeLineAll("-- Logged on channel %02d: %s/%s" % 
                (client.channel.number, client.user.id, client.user.handle))
        return True
        
    def removeClient(self, client):
        self._clients.remove(client)
        self.writeLineAll("-- DISCOnnected! channel %02d: %s/%s" % 
                (client.channel.number, client.user.id, client.user.handle))
        return True
    
    def lineReceived(self, client, line):
        self.writeLineChannelFormatted(client, line)
        
    def writeLineAllFormatted(self, fromclient, line):
        for c in self._clients:
            c.writeLine(c.user.formatMessage(fromclient.user, line))
        
    def writeLineChannelFormatted(self, fromclient, line):
        # TODO
        self.writeLineAllFormatted(fromclient, line)

    def writeLineAll(self, line):
        for c in self._clients:
            c.writeLine(line)
    
    def writeLineChannel(self, fromclient, line):
        # TODO
        self.writeLineAll(line)

