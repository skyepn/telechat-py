# ----------------------------------------------------------------------------
# config.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

import telechat.db

class TCConfig:
    # Borg (Monostate) Singleton pattern
    __shared_state = {}
    
    def __init__(self, filename=None):
        # Monostate
        self.__dict__ = self.__shared_state
        # Already loaded?
        if 'filename' in self.__dict__:
            return
        self.filename = filename

        # TODO config
        dbname = "db/f4/telechat.db" 
        self.db = telechat.db.TCDB(dbname)
        
        # TODO getattr check if file has changed
        self.prelogin_msg = open("db/f4/prelogin.msg").read()
        self.postlogin_msg = open("db/f4/postlogin.msg").read()
