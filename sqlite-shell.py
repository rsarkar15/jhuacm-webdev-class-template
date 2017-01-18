#!/usr/bin/env python3

import sqlite3

db = sqlite3.connect('database.sqlite3')

while True:
    cmd = input("sqlite3> ")
    cur = db.cursor()
    try:
        cur.execute(cmd)
        db.commit()
        out = cur.fetchall()
        if out is not None:
            for x in out:
                print(repr(x))
    except Exception as e:
        print(e)
    finally:
        cur.close()
