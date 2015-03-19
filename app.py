# all the imports
import sqlite3,re
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing

# configuration
DATABASE = '/home/flavorshare/mysite/flavorshare.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def main_page():
    error = None
    return render_template('login_or_register.html')


@app.route('/', methods=['POST'])
def login_or_register():
    error = None
    if request.method == 'POST':
        if request.form['login_register'] == "Login":
                pageFunctionName='loginPage'
        elif request.form['login_register'] == "Register":
                pageFunctionName='registerPage'
    return redirect(url_for(pageFunctionName))

@app.route('/register')
def registerPage():
    error = None
    return render_template('register.html')

EMAIL_REGEX = re.compile(r"[^@|\s]+@[^@]+\.[^@|\s]+")

@app.route('/register', methods=['POST'])
def register():
    error = None
    if request.method == 'POST':
        if request.form['register'] == "Register":
            if request.form['password'] == request.form['confirm_password'] and EMAIL_REGEX.match(request.form['email']) :
                g.db.execute('insert into users (name, email, password) values (?, ?, ?)',
                         [request.form['name'], request.form['email'], request.form['password']])
                g.db.commit()
                flash('Successfully Registered')
                return redirect(url_for('homePage'))
            else :
                flash('Incorrect Details')
                return redirect(url_for('register'))



@app.route('/login')
def loginPage():
    error = None
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['login'] == "Login":
            cur = g.db.execute('select name, password from users where name = \"' + request.form['username'] + '\" and password = \"' + request.form['password'] + '\"')
            if cur is not None:
                flash('Successfully Logged In')
                return redirect(url_for('homePage'))
            if cur is None:
                flash('Invalid Log In')
                return render_template('login.html')

@app.route('/home')
def homePage():
    error = None
    return render_template('home.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
