# ----------------------------------------------------------------------------
# telechat.tac
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

#import sys
#sys.path.append('.')

from twisted.application import internet
from twisted.application import service
import telechat.factory
import telechat.cred
import telechat.const
import telechat.config

PORT = 8023  # TODO config file

# ----------------------------------------------------------------------------

r = telechat.cred.TCRealm()
config = telechat.config.TCConfig('TODO')
p = telechat.cred.createPortal(r)

application = service.Application(telechat.const.APPNAME + " Server")
f = telechat.factory.TelechatFactory(p)
f.protocol.factory = f
tcService = internet.TCPServer(PORT, f)
tcService.setServiceParent(application)
