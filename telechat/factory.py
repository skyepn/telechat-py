# ----------------------------------------------------------------------------
# factory.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from twisted.internet.protocol import ServerFactory
from twisted.conch.telnet import TelnetTransport
from telechat.protocol import TSAuthenticatingTelnetProtocol
from telechat.config import TCConfig
from telechat import channel

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
    _channels   = []
    
    def __init__(self, portal):
        self._portal = portal
        self.protocol = lambda:TelnetTransport(TSAuthenticatingTelnetProtocol, self._portal)
        self._addStandardChannels()
        
    def isConnectionAllowed(self, client):
        if len(self._clients) > MAX_CLIENTS:
            print "Reached max clients %d, rejecting connection from %s" % (MAX_CLIENTS, client.transport.getPeer().host)
            return False
        return True
        
    # --------------------------------------------------------------
    
    def addClient(self, client):
        # TODO check for duplicate user, kick off old (frozen) login
        self._clients.append(client)
        self.writeLineAll("-- Logged on channel %s: %s/%s" % (client.channel.nameToStr(), client.user.id, client.user.handle))
        return True
        
    def removeClient(self, client):
        channelstr = 'None'
        if client.channel:
            if client.channel.title is not None:
                channelstr = client.channel.nameToStr()
            else:
                channelstr = '<private>'
            self.leaveChannel(client, client.channel, False)
        if client.user.cleanQuit:
            self.writeLineAll("-- Logged off channel %s: %s/%s" % (channelstr, client.user.id, client.user.handle))
        else:
            self.writeLineAll("-- DISCOnnected! channel %s: %s/%s" % (channelstr, client.user.id, client.user.handle))
        self._clients.remove(client)
        return True
    
    # --------------------------------------------------------------

    def _addStandardChannels(self):
        # Create persistent channels
        chan = channel.TCNumberedChannel(1)
        chan.title = 'Main Floor'
        chan.persist = True
        self._channels.append(chan)
        chan = channel.TCNumberedChannel(2)
        chan.title = 'Chillout Room'
        chan.persist = True
        self._channels.append(chan)
        
    def findChannel(self, name):
        for chan in self._channels:
            if chan.name == name:
                return chan
        return None
        
    def joinChannel(self, client, chname, showMessage=True):
        chname = channel.TCNumberedChannel.nameTransform(chname)
        print "joinChannel user", client.user.id, "chname", chname
        chan = self.findChannel(chname)
        if chan is not None:
            if chan == client.channel:
                raise Exception('You are already on that channel.')
        else:
            # Create a new channel
            chan = channel.TCNumberedChannel(chname)
            self._channels.append(chan)
        chan.users.append(client.user)
        if showMessage:
            self.writeLineChannel(client, chan, "-- Joined channel %s: %s/%s" % (chan.nameToStr(), client.user.id, client.user.handle), True)
        print "leaveChannel _channels now:\n\t", '\n\t'.join(map(str, self._channels))
        return chan
    
    def leaveChannel(self, client, chan, showMessage=True):
        print "user", client.user.id, "left channel", chan.name
        if client.user not in chan.users:
            raise KeyError, 'User not in channel!'
        if chan not in self._channels:
            raise KeyError, 'That channel does not exist!'
        chan.users.remove(client.user)
        if showMessage:
            self.writeLineChannel(client, chan, "-- Left channel %s: %s/%s" % (chan.nameToStr(), client.user.id, client.user.handle), True)
        if len(chan.users) == 0 and not chan.persist:
            # Remove the channel
            print "leaveChannel destroy", chan.name
            self._channels.remove(chan)
        print "leaveChannel _channels now:\n\t", '\n\t'.join(map(str, self._channels))
    
    # --------------------------------------------------------------

    def lineReceived(self, fromclient, line):
        self.writeLineChannelFormatted(fromclient, fromclient.channel, line)
        
    def writeLineAll(self, line):
        for c in self._clients:
            c.writeLine(line)
    
    def writeLineAllFormatted(self, fromclient, line):
        for c in self._clients:
            c.writeLine(c.user.formatMessage(fromclient.user, line))
        
    def writeLineChannel(self, fromclient, chan, line, noEcho=False):
        for user in chan.users:
            if noEcho and user.client == fromclient:
                continue
            user.client.writeLine(line)

    def writeLineChannelFormatted(self, fromclient, chan, line, noEcho=False):
        for user in chan.users:
            if noEcho and user.client == fromclient:
                continue
            user.client.writeLine(user.formatMessage(fromclient.user, line))

