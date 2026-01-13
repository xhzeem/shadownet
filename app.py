from flask import Flask, request, render_template_string, render_template, redirect, url_for, session, send_from_directory
import sqlite3
import os
import subprocess
import requests
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_PATH = '/tmp/shadowwork.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = get_db()
    # Core User Table
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, bio TEXT, role TEXT)')
    # Task Manager (Stored XSS)
    conn.execute('CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, content TEXT, status TEXT)')
    # Expense Vault (SQLi / IDOR)
    conn.execute('CREATE TABLE expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, category TEXT, amount REAL, description TEXT, receipt_id TEXT)')
    
    # Mock Data
    users = [
        (1, 'admin', 'admin123', 'Director of Operations at ShadowWork.', 'Admin'),
        (2, 'j.doe', 'secret123', 'Software Engineer specialized in internal tools.', 'User'),
        (3, 'b.wayne', 'nananana', 'Executive Consultant.', 'VIP')
    ]
    for u in users:
        conn.execute('INSERT INTO users (id, username, password, bio, role) VALUES (?,?,?,?,?)', u)
    
    tasks = [
        (1, 'Audit Internal Systems', 'Schedule a deep audit of the new gateway.', 'Pending'),
        (2, 'Fix Sidebar Bug', 'The sidebar collapses unexpectedly on mobile.', 'In Progress')
    ]
    for t in tasks:
        conn.execute('INSERT INTO tasks (user_id, title, content, status) VALUES (?,?,?,?)', t)
        
    expenses = [
        (1, 'Infrastructure', 1250.50, 'Monthly AWS Cloud Hosting', 'REC_A01'),
        (2, 'Learning', 45.00, 'Security Research Subscription', 'REC_B02')
    ]
    for e in expenses:
        conn.execute('INSERT INTO expenses (user_id, category, amount, description, receipt_id) VALUES (?,?,?,?,?)', e)

    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    task_count = conn.execute('SELECT COUNT(*) FROM tasks WHERE user_id = ?', (session['user_id'],)).fetchone()[0]
    expense_sum = conn.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ?', (session['user_id'],)).fetchone()[0] or 0
    conn.close()
    
    return render_template('dashboard.html', user=user, task_count=task_count, expense_sum=expense_sum)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # VULNERABILITY: SQL Injection (Login Bypass)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = get_db()
        try:
            user = conn.execute(query).fetchone()
            if user:
                session['user_id'] = user['id']
                return redirect(url_for('index'))
            else:
                error = "Invalid credentials."
        except Exception as e:
            error = f"Database Error: {e}"
        finally:
            conn.close()
    return render_template('login.html', error=error)

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # VULNERABILITY: Stored XSS (content field is safe-filtered in template)
        conn.execute('INSERT INTO tasks (user_id, title, content, status) VALUES (?, ?, ?, ?)', 
                     (session['user_id'], title, content, 'Open'))
        conn.commit()
        
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('tasks.html', tasks=tasks)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    
    # VULNERABILITY: SQL Injection (Search parameter)
    search = request.args.get('q', '')
    if search:
        query = f"SELECT * FROM expenses WHERE user_id = {session['user_id']} AND description LIKE '%{search}%'"
        expenses = conn.execute(query).fetchall()
    else:
        expenses = conn.execute('SELECT * FROM expenses WHERE user_id = ?', (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('expenses.html', expenses=expenses)

@app.route('/receipt/<receipt_id>')
def view_receipt(receipt_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    # VULNERABILITY: IDOR (No check if the receipt belongs to the user)
    conn = get_db()
    expense = conn.execute('SELECT * FROM expenses WHERE receipt_id = ?', (receipt_id,)).fetchone()
    conn.close()
    if expense:
        return render_template('receipt.html', expense=expense)
    return "Receipt not found", 404

@app.route('/integrations', methods=['GET', 'POST'])
def integrations():
    if 'user_id' not in session: return redirect(url_for('login'))
    content = ""
    if request.method == 'POST':
        url = request.form['url']
        # VULNERABILITY: SSRF
        try:
            res = requests.get(url, timeout=5)
            content = res.text
        except Exception as e:
            content = f"Connection failed: {e}"
    return render_template('integrations.html', content=content)

@app.route('/admin/maintenance', methods=['GET', 'POST'])
def maintenance():
    # In a real app, we'd check if user is admin, but for CTF we might leave it open or weak
    if 'user_id' not in session: return redirect(url_for('login'))
    output = ""
    if request.method == 'POST':
        tool = request.form['tool']
        target = request.form['target']
        # VULNERABILITY: RCE
        if tool == 'check':
            cmd = f"ping -c 2 {target}"
            try:
                output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
            except Exception as e:
                output = str(e)
    return render_template('maintenance.html', output=output)

@app.route('/settings')
def settings():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_pref = request.args.get('theme', 'Standard')
    
    # VULNERABILITY: SSTI (The parameter is injected directly into a template string)
    # We use a helper template to show the UI, but the "display" part is vulnerable
    display_template = f"<span>{user_pref}</span>"
    theme_display = render_template_string(display_template)
    
    return render_template('settings.html', theme=user_pref, theme_display=theme_display)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
