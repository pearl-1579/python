from flask import Flask, render_template, request, g
import sqlite3
import os
import datetime
import random

app = Flask(__name__)

# Define the path to the database file
DATABASE = os.path.join(app.root_path, 'submissions.db')

# List of random quotes
quotes = [
    "The best way to predict the future is to create it.",
    "You miss 100% of the shots you don't take.",
    "Success is not final, failure is not fatal: It is the courage to continue that counts.",
    "Believe you can and you're halfway there.",
    "Don't watch the clock; do what it does. Keep going."
]

# Function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Return rows that behave like dicts
    return db

# Teardown function to close database connection
@app.teardown_appcontext
def close_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Check if the database exists before each request
@app.before_request
def before_request():
    if not os.path.exists(DATABASE):
        init_db()

# Example route to demonstrate usage
@app.route('/')
def index():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    quote = random.choice(quotes)
    return render_template('index.html', current_time=current_time, quote=quote)

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    email = request.form['email']
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO submissions (name, email, timestamp) VALUES (?, ?, ?)', (name, email, timestamp))
    db.commit()

    return render_template('submit.html', name=name, email=email, timestamp=timestamp)

# Route to display all submissions
@app.route('/submissions')
def submissions():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT name, email, timestamp FROM submissions ORDER BY timestamp DESC')
    submissions = cursor.fetchall()
    return render_template('submissions.html', submissions=submissions)

if __name__ == '__main__':
    app.run(debug=True)
