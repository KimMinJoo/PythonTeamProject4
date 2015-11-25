import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
abort, render_template, flash
from contextlib import closing
# configuration
DATABASE = 'flask.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'
app = Flask(__name__) 
app.config.from_object(__name__)
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()
@app.before_request #request호출 전
def before_request():
    g.db = connect_db()
@app.teardown_request #request의 마지막에 호출
def teardown_request(exception):
    g.db.close()
@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text,id from entries order by id desc')
    entries = [dict(title=row[0], text=row[1],id= row[2]) for row in cur.fetchall()]
    length = len(entries)
    #print(entries) # 그냥 찍어보는구문!
    return render_template('show_entries.html', entries=entries,length=length)
@app.route('/add', methods=['POST'])
def add_entry():
    if request.form['updateflag'] == "none":
        g.db.execute('insert into entries (title, text) values (?, ?)', [request.form['NoteTitle'], request.form['NoteTextarea']])
        g.db.commit()
        flash('New entry was successfully posted')
    else:
        g.db.execute("UPDATE entries SET title = ? ,text = ? WHERE id= ?", [request.form['NoteTitle'], request.form['NoteTextarea'],request.form['updateflag']])
        g.db.commit()
        flash('Entry was successfully updated')
    return redirect(url_for('show_entries'))
if __name__=='__main__':
    init_db()
    app.run()