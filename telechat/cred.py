# ----------------------------------------------------------------------------
# cred.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from zope.interface import implements
from twisted.conch.telnet import ITelnetProtocol
from telechat.protocol import TCSimpleProtocol
from twisted.cred.portal import IRealm, Portal
from twisted.cred import checkers
from twisted.cred import credentials

# ----------------------------------------------------------------------------

class TCRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if ITelnetProtocol in interfaces:
            avatar = TCSimpleProtocol(avatarId)
            return ITelnetProtocol, avatar, lambda:None
        else:
            raise NotImplementedError("Not supported by this realm")

# ----------------------------------------------------------------------------

def createPortal(realm):
    p = Portal(realm)
    c = checkers.InMemoryUsernamePasswordDatabaseDontUse()
    c.addUser("foo", "pass")
    c.addUser("bar", "pass")
    p.registerChecker(c)
    p.registerChecker(checkers.AllowAnonymousAccess())
    return p