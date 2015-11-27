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
def mainpage():
    return render_template('login.html')
@app.route('/login', methods=['POST'])
def login():
    cur = g.db.execute('select * from Member where id=?',request.form['userid'])
    if len(cur.fetchall())==0:
        flash('아이디를 확인해주세요')
        return render_template('login.html')
    cur = g.db.execute('select * from Member where id=? and passwd =?',[request.form['userid'], request.form['userpasswd']])
    if len(cur.fetchall())==0:
        flash('비밀번호를 확인해주세요')
        return render_template('login.html')
    else:
        flash('Login성공')
        session['id'] = request.form['userid']
        return redirect(url_for('show_entries'))
        '''
    if request.form['userid']=="admin":
        if request.form['userpasswd']=="123":
            flash('Login성공')
            session['id'] = request.form['userid']
            return redirect(url_for('show_entries'))
        else:
            flash('비밀번호를 확인해주세요')
            return render_template('login.html')
    else:
        flash('아이디를 확인해주세요')
        return render_template('login.html')
        '''
@app.route('/logout',methods=['POST'])
def logout():
    session.pop('id', None)
    flash('You were logged out')
    return redirect(url_for('mainpage'))
@app.route('/insertmember',methods=['POST'])
def insertMember():
    if len(request.form['userid'])==0:
        flash('아이디를 입력해주세요.')
        return redirect(url_for('mainpage'))
    elif len(request.form['userpasswd'])==0:
        flash('비밀번호를 입력해주세요.')
        return redirect(url_for('mainpage'))
    cur = g.db.execute('select * from Member where id=?',request.form['userid'])
    if len(cur.fetchall())==0:
            g.db.execute('insert into Member (id, passwd) values (?, ?)', [request.form['userid'], request.form['userpasswd']])
            g.db.commit()
            flash('New Member was successfully inserted')
    else:
        flash('아이디가 이미 존재합니다.')
    return redirect(url_for('mainpage'))
@app.route('/Note')
def show_entries():
    cur = g.db.execute('select title, text, id,userid from entries where userid=? order by id desc',session['id'])
    entries = [dict(title=row[0], text=row[1],id= row[2],userid=row[3]) for row in cur.fetchall()]
    list=[]
    for item in entries:
        flag=True
        str1=item['text']
        if str1=="<br>":
            str1=" ";
            list.append(str1)
            flag=False
        if str1[0]!="<":
            flag=False
            list.append(str1)
        while flag:
            first = str1[0]
            if first=="<":
                for i in range(len(str1)):
                    if str1[i]==">":
                        str1= str1[i+1:]
                        break
            else:
                for i in range(len(str1)):
                    if str1[i]=="<":
                        str1= str1[:i]
                        flag=False;
                        break
        list.append(str1)
    length = len(entries)
    #print(entries) # 그냥 찍어보는구문!
    return render_template('show_entries.html', entries=entries,length=length,text = list)
@app.route('/add', methods=['POST'])
def add_entry():
    str1 = str(request.form['NoteTextarea'])
    if len(request.form['NoteTitle'])==0:
        flash('제목을 입력해주세요')
        return redirect(url_for('show_entries'))
    if len(str1)==0 or str1=="<br>":
        flash('내용을 입력해주세요')
        return redirect(url_for('show_entries'))
    for i in range(len(str1)):
        if str1[i] == "\"":
            str1=str1[:i]+"'"+str1[i+1:]
    if request.form['updateflag'] == "none":
        g.db.execute('insert into entries (title, text, userid) values (?, ?, ?)', [request.form['NoteTitle'], str1, session['id']])
        g.db.commit()
        flash('New entry was successfully posted')
    else:
        g.db.execute("UPDATE entries SET title = ? ,text = ? WHERE id= ?", [request.form['NoteTitle'],str1,request.form['updateflag']])
        g.db.commit()
        flash('Entry was successfully updated')
    return redirect(url_for('show_entries'))
@app.route('/del/<id>')
def del_entry(id):
    g.db.execute('delete from entries where id=?',[id])
    g.db.commit()
    flash('Entry was successfully deleted')
    return redirect(url_for('show_entries'))


if __name__=='__main__':
    #init_db()
    app.run()