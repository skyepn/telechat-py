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
    id = None

    def __init__(self, username):
        TCConfig().db.loadUser(username, self)
        #print "TCUser loaded:", self, self.__dict__
    
    def formatMessage(self, fromuser, message):
        # TODO parse self.fmt_message
        # TODO word wrap
        return "%s/%s: %s" % (fromuser.id, fromuser.handle, message)
    