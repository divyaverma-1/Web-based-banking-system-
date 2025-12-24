from flask import Flask, render_template, request, redirect, url_for
import json, os

app = Flask(__name__)
DATA_FILE = "bank_data.json"

# --- Helper functions ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "admin": {"username": "admin", "password": "admin"}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Routes ---
@app.route('/')
def home():
    return render_template("index.html")

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    data = load_data()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in data["users"]:
            return "Username already exists! <a href='/register'>Try again</a>"
        data["users"][username] = {"password": password, "balance": 0.0}
        save_data(data)
        return redirect(url_for('login'))
    return render_template("register.html")

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    data = load_data()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == data["admin"]["username"] and password == data["admin"]["password"]:
            return redirect(url_for('admin_menu'))
        user = data["users"].get(username)
        if user and user["password"] == password:
            return redirect(url_for('user_menu', username=username))
        else:
            return "Invalid credentials! <a href='/login'>Try again</a>"
    return render_template("login.html")

# User menu
@app.route('/user/<username>', methods=['GET', 'POST'])
def user_menu(username):
    data = load_data()
    user = data["users"].get(username)
    if not user:
        return "User not found!"

    message = ""
    if request.method == 'POST':
        action = request.form['action']
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                message = "Amount must be positive."
            elif action == 'deposit':
                user['balance'] += amount
                message = f"Deposited ₹{amount} successfully."
            elif action == 'withdraw':
                if amount > user['balance']:
                    message = "Insufficient balance!"
                else:
                    user['balance'] -= amount
                    message = f"Withdrew ₹{amount} successfully."
            elif action == 'transfer':
                recipient = request.form['recipient']
                if recipient not in data['users']:
                    message = "Recipient not found!"
                elif amount > user['balance']:
                    message = "Insufficient balance!"
                else:
                    user['balance'] -= amount
                    data['users'][recipient]['balance'] += amount
                    message = f"Transferred ₹{amount} to {recipient}."
            save_data(data)
        except ValueError:
            message = "Invalid amount!"
    return render_template("user_menu.html", username=username, balance=user['balance'], message=message)

# Admin menu
@app.route('/admin', methods=['GET', 'POST'])
def admin_menu():
    data = load_data()
    message = ""
    if request.method == 'POST':
        del_user = request.form.get('delete_user')
        if del_user in data["users"]:
            del data["users"][del_user]
            save_data(data)
            message = f"User '{del_user}' deleted."
        else:
            message = "User not found!"
    users = data["users"]
    return render_template("admin_menu.html", users=users, message=message)

if __name__ == '__main__':
    app.run(debug=True)
