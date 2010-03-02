# ----------------------------------------------------------------------------
# cred.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

import crypt
from telechat import protocol
from telechat.config import TCConfig
from zope.interface import implements
from twisted.conch import telnet
from twisted.internet import defer
from twisted.cred import portal, checkers, credentials, error

CRYPT_SALT = 'XX' # historical...

# ----------------------------------------------------------------------------

class TCRealm:
    implements(portal.IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        if telnet.ITelnetProtocol in interfaces:
            avatar = protocol.TCSimpleProtocol(avatarId)
            return telnet.ITelnetProtocol, avatar, lambda:None
        else:
            raise NotImplementedError("Not supported by this realm")
            
# ----------------------------------------------------------------------------

def hash_password_crypt(username, checkpass, userpass):
    return crypt.crypt(checkpass, CRYPT_SALT)

# ----------------------------------------------------------------------------

class TCDBChecker:
    implements(checkers.ICredentialsChecker)
    credentialInterfaces = (credentials.IUsernamePassword,)

    _hashf = None
    
    def __init__(self):
        self._hashf = hash_password_crypt

    def _cbPasswordMatch(self, matched, username):
        if matched:
            return username
        else:
            return failure.Failure(error.UnauthorizedLogin())

    def requestAvatarId(self, creds):
        try:
            password = TCConfig().db.getUserValue(creds.username, 'password')
        except KeyError:
            return defer.fail(error.UnauthorizedLogin())
        else:
            up = credentials.IUsernamePassword(creds, None)
            if up is None:
                return defer.fail(error.UnauthorizedLogin())
            hashed = self._hashf(up.username, up.password, password)
            #print "requestAvatarId: check pass", hashed, password
            if hashed == password:
                return defer.succeed(creds.username)
            return defer.fail(error.UnauthorizedLogin())

# ----------------------------------------------------------------------------

def createPortal(realm):
    p = portal.Portal(realm)
#    c = checkers.InMemoryUsernamePasswordDatabaseDontUse()
#    c.addUser("foo", "pass")
    c = TCDBChecker()
    p.registerChecker(c)
    return p
