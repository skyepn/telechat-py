# ----------------------------------------------------------------------------
# telechat.tac
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

#import sys
#sys.path.append('.')

from twisted.application.internet import TCPServer
from twisted.application.service import Application
from telechat.factory import TelechatFactory
from telechat.cred import TCRealm, createPortal

PORT = 8023  # TODO config file

# ----------------------------------------------------------------------------

r = TCRealm()
p = createPortal(r)

application = Application("Telechat Server")
f = TelechatFactory(p)
f.protocol.factory = f
tcService = TCPServer(PORT, f)
tcService.setServiceParent(application)
