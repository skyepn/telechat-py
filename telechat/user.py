# ----------------------------------------------------------------------------
# user.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

from telechat.config import TCConfig

class TCUser:
    id = None

    def __init__(self, username):
        TCConfig().db.loadUser(username, self)
        print "Hi I'm a TCUser!", self, self.__dict__
    
    def formatMessage(self, fromuser, message):
        # TODO parse self.fmt_message
        # TODO word wrap
        return "%s/%s: %s" % (fromuser.id, fromuser.handle, message)
    