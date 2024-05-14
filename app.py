from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.your_database_name
users = db.users

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users.find_one({'username': username, 'password': password})

    if user:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid username/password'

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome {session['username']}!"
    else:
        return redirect(url_for('index'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users.insert_one({'username': username, 'password': password})
        return redirect(url_for('index'))
    return render_template('create_account.html')

if __name__ == '__main__':
    app.run(debug=True)
