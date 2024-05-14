from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your_secret_key'

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.your_database_name
users = db.users
payments = db.payments  # New collection for payments

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = users.find_one({'username': username})

    if user and bcrypt.check_password_hash(user['password'], password):
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid username/password'

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        username = session['username']
        pending_payments = payments.find({'to_user': username, 'status': 'pending'})
        return render_template('dashboard.html', username=username, payments=pending_payments)
    else:
        return redirect(url_for('index'))

@app.route('/request_payment', methods=['POST'])
def request_payment():
    from_user = session['username']
    to_user = request.form['to_user']
    amount = request.form['amount']

    # Check if the recipient exists
    if users.find_one({'username': to_user}):
        payment = {
            'from_user': from_user,
            'to_user': to_user,
            'amount': amount,
            'status': 'pending'
        }
        payments.insert_one(payment)
        return redirect(url_for('dashboard'))
    else:
        return 'User does not exist'

@app.route('/complete_payment', methods=['POST'])
def complete_payment():
    payment_id = request.form['payment_id']
    payments.update_one({'_id': payment_id}, {'$set': {'status': 'completed'}})
    return redirect(url_for('dashboard'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('index'))
    return render_template('create_account.html')

if __name__ == '__main__':
    app.run(debug=True)
