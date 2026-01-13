from flask import Flask, request, render_template_string, render_template, redirect, url_for, session
import sqlite3
import os
import subprocess
import requests

app = Flask(__name__)
app.secret_key = 'super-secret-key-that-should-be-hidden-but-isnt'

# Database setup
DB_PATH = '/tmp/shadownet.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, bio TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, content TEXT)')
    conn.execute("INSERT OR IGNORE INTO users (id, username, password, bio) VALUES (1, 'admin', 'admin123', 'I am the overlord.')")
    conn.execute("INSERT OR IGNORE INTO users (id, username, password, bio) VALUES (2, 'guest', 'guest', 'Just a visitor.')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = get_db()
        try:
            user = conn.execute(query).fetchone()
        except Exception as e:
            error = str(e)
            user = None
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            return redirect(url_for('profile', user_id=user['id']))
        elif not error:
            error = 'Invalid credentials'
    return render_template('login.html', error=error)

@app.route('/guestbook', methods=['GET', 'POST'])
def guestbook():
    conn = get_db()
    if request.method == 'POST':
        content = request.form['content']
        conn.execute('INSERT INTO comments (content) VALUES (?)', (content,))
        conn.commit()
    comments = conn.execute('SELECT * FROM comments').fetchall()
    conn.close()
    return render_template('guestbook.html', comments=comments)

@app.route('/profile/<int:user_id>')
def profile(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return render_template('profile.html', user=user)
    return "User not found", 404

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    output = ""
    if request.method == 'POST':
        ip = request.form['ip']
        command = f"ping -c 3 {ip}"
        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode()
        except subprocess.CalledProcessError as e:
            output = e.output.decode()
    return render_template('ping.html', output=output)

@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    content = ""
    if request.method == 'POST':
        url = request.form['url']
        try:
            response = requests.get(url, timeout=5)
            content = response.text
        except Exception as e:
            content = str(e)
    return render_template('fetch.html', content=content)

@app.route('/greet')
def greet():
    name = request.args.get('name', 'Guest')
    template = f"<h1>Hello, {name}!</h1>"
    return render_template_string(template)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
