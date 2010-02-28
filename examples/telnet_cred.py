# http://www.mail-archive.com/twisted-python@twistedmatrix.com/msg01581.html

import sys
from zope.interface import implements
from twisted.internet import protocol
from twisted.python import log
from twisted.cred import error
from twisted.cred import portal
from twisted.cred import checkers
from twisted.cred import credentials
from twisted.conch.telnet import AuthenticatingTelnetProtocol
from twisted.conch.telnet import StatefulTelnetProtocol
from twisted.conch.telnet import ITelnetProtocol
from twisted.conch.telnet import TelnetTransport

class Realm:
  implements(portal.IRealm)

  def requestAvatar(self, avatarId, mind, *interfaces):
    if ITelnetProtocol in interfaces:
      av = MyTelnet()
      av.state = 'Command'
      return ITelnetProtocol, av, lambda:None
    raise NotImplementedError("Not supported by this realm")

class MyTelnet(StatefulTelnetProtocol):
  def telnet_Command(self, line):
    print "recv", line

def main():
  r = Realm()
  p = portal.Portal(r)
  c = checkers.InMemoryUsernamePasswordDatabaseDontUse()
  c.addUser("user", "pass")
  p.registerChecker(c)
  p.registerChecker(checkers.AllowAnonymousAccess())
  f = protocol.ServerFactory()
  f.protocol = lambda: TelnetTransport(AuthenticatingTelnetProtocol, p)
  log.startLogging(sys.stdout)
  from twisted.internet import reactor
  reactor.listenTCP(4738, f)
  reactor.run()

if __name__ == '__main__':
  main()
