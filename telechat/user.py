# ----------------------------------------------------------------------------
# user.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from telechat.config import TCConfig

USER_LEVEL_NEW      = 0
USER_LEVEL_REGULAR  = 1
USER_LEVEL_2        = 2
USER_LEVEL_3        = 3
USER_LEVEL_POWER    = 4
USER_LEVEL_ADMIN    = 5

# ----------------------------------------------------------------------------

class TCUser:
    id          = None
    client      = None
    cleanQuit   = False

    def __init__(self, username, client):
        TCConfig().db.loadUser(username, self)
        #print "TCUser loaded:", self, self.__dict__
        self.client = client
        
    def __str__(self):
        return self.id
    
    def formatMessage(self, user, message):
        # TODO parse self.fmt_message
        # TODO word wrap
        return "%s/%s: %s" % (user.id, user.handle, message)

    def formatWho(self, user):
        # TODO parse self.fmt_active
        return "%s/%s [%s] todo" % (user.id, user.handle, user.email)

