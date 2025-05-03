from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)

# Helper to get user's notes
def load_user_notes(username):
    path = f'data/{username}.txt'
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        lines = [line.strip().split('|', 1) for line in f.readlines()]
    return lines

# Home page
@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    notes = load_user_notes(session['username'])
    return render_template('index.html', photo_notes=notes, username=session['username'])

# Upload photo + note
@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    photo = request.files['photo']
    note = request.form['note']
    if photo:
        filename = photo.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(path)

        # Save entry
        with open(f'data/{session["username"]}.txt', 'a') as f:
            f.write(f'{filename}|{note}\n')

    return redirect(url_for('index'))

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        with open('users.txt', 'r') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) != 2:
                    continue  # skip malformed lines
                user, pw = parts
                if user == uname and pw == pwd:
                    session['username'] = uname
                    return redirect(url_for('index'))


    return render_template('login.html')

# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']

        # Save new user
        with open('users.txt', 'a') as f:
            f.write(f'{uname}|{pwd}\n')

        # Log in after registering
        session['username'] = uname
        return redirect(url_for('index'))

    return render_template('register.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

