#!/usr/bin/env python3

import os
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, url_for, request, g
app = Flask(__name__)

class DatabaseWrapper(object):
    """We cried, so you don't have to."""
    def __init__(self, db):
        self.db = db
    def close(self): self.db.close()
    def _fix(self, x): return x
    def select(self, query, args=[]):
        cur = self.db.cursor()
        cur.execute(self._fix(query), args)
        out = cur.fetchall()
        cur.close()
        return out
    def execute(self, query, args=[]):
        cur = self.db.cursor()
        cur.execute(self._fix(query), args)
        self.db.commit()
        cur.close()

if 'DATABASE_URL' in os.environ:
    import psycopg2
    import urllib.parse
    urllib.parse.uses_netloc.append("postgres")
    db_url = urlparse(os.environ["DATABASE_URL"])
    DatabaseWrapper._fix = lambda self, x: x.replace('?', '%s')
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = psycopg2.connect(
                database=db_url.path[1:],
                user=db_url.username,
                password=db_url.password,
                host=db_url.hostname,
                port=db_url.port
            )
        
        return DatabaseWrapper(db)
else:
    import sqlite3
    def get_db():
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect('database.sqlite3')
        return DatabaseWrapper(db)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

######################################################################
###### The stuff above is a library to make things work easily. ######
######################################################################

from datetime import datetime

@app.route('/add_meme', methods=['POST'])
def add_meme():
    get_db().execute('INSERT INTO memes(url, caption1, caption2) VALUES(?, ?, ?);', [
        request.form['image'],
        request.form['top_caption'],
        request.form['bottom_caption']
    ])
    return redirect(url_for('index'))

@app.route('/meme/<id>')
def show(id):
    the_list = get_db().select('SELECT id,url,caption1,caption2 FROM memes WHERE id=?;', [int(id)])
    meme = the_list[0]
    meme_img = meme[1]
    top_caption = meme[2]
    bottom_caption = meme[3]
    return render_template(
        'show.html',
        meme_img = meme_img,
        top_caption = top_caption,
        bottom_caption = bottom_caption
    )

@app.route('/meme_form')
def meme_form():
    return render_template('meme-form.html')

@app.route('/')
def index():
    #return str(datetime.now())
    memes = []
    for row in get_db().select('SELECT id,url,caption1,caption2 FROM memes ORDER BY id DESC;'):
        memes.append({
            'image': row[1],
            'top_caption': row[2],
            'bottom_caption': row[3],
            'id': row[0]
        })
    return render_template('homepage.html', memes = memes)
    #up_to = int(request.args['count'])
    #out = "<ul>"
    #for i in range(up_to):
    #    out += "<li>" + str(i) + "</li>"
    #out += "</ul>"
    #return out

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host=os.environ.get('BIND_TO', '127.0.0.1'), port=port, debug=bool(int(os.environ.get('FLASK_DEBUG', 1))))
