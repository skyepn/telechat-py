# ----------------------------------------------------------------------------
# db.py
# ----------------------------------------------------------------------------
# Copyright (c) 2010 Skye Nott
# See LICENSE for details.

import sqlite3

# TODO persistent squelch/reverse
# TODO add user disabled (security)

USER_TABLE = 'users'
VALID_COLUMNS = (
    'password',
) # for getUserValue

SCHEMA = """
CREATE TABLE users (
        id          TEXT PRIMARY KEY NOT NULL,
        password    TEXT NOT NULL,
        handle      TEXT NOT NULL,
        channel     INTEGER NOT NULL,
        timezone    INTEGER NOT NULL,
        width       INTEGER,
        level       INTEGER NOT NULL,
        nlchar      TEXT NOT NULL,
        fmt_active      TEXT,
        fmt_message     TEXT,
        email           TEXT NOT NULL,
        email_public    INTEGER NOT NULL,
        created_ip      TEXT NOT NULL,
        ts_created      INTEGER,
        ts_last_logout  INTEGER,
        verified        INTEGER NOT NULL
    );
"""

# ----------------------------------------------------------------------------

class TCDB:
    
    _dbcon = None
    _dbcur = None
    
    def __init__(self, filename):
        self._dbcon = sqlite3.connect(filename)
        self._dbcon.row_factory = sqlite3.Row
        self._dbcon.text_factory = sqlite3.OptimizedUnicode
        self._dbcur = self._dbcon.cursor()
                
    def __del__(self):
        print "destructor, closing DB connection"
        if self._dbcon is not None:
            self._dbcon.close()
        
    def getUserValue(self, username, colname):
        username = username.lower()
        if colname not in VALID_COLUMNS:
            raise IndexError, "bad column %s" % colname
        self._dbcur.execute("select %s from %s where id=?" % (colname, USER_TABLE), (username,))
        row = self._dbcur.fetchone()
        if row is None:
            raise KeyError(username)
        return row[0]

    def loadUser(self, username, user):
        username = username.lower()
        self._dbcur.execute("select * from %s where id=?" % USER_TABLE, (username,))
        row = self._dbcur.fetchone()
        if row is None:
            raise KeyError(username)
        for colname in row.keys():
            #print "loadUser: setting", user, colname, row[colname]
            setattr(user, colname, row[colname])




