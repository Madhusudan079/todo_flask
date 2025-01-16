from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pymongo import MongoClient
import certifi 
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
import random
import re

a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

SECRET_KEY = ''.join(random.choices(a, k=16))
serializer = URLSafeTimedSerializer(SECRET_KEY)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['user_auth_db']
collection = db['users']

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'supersecretkey'  # Secret key for sessions

db = SQLAlchemy(app)

# Define the ToDo model
class ToDo(db.Model):
    sNo = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now().replace(microsecond=0))    

    def __repr__(self):
        return f"{self.sNo} - {self.title} - {self.desc}"

# Create the database tables
with app.app_context():
    db.create_all()

EMAIL_ADDRESS = 'madhusudan07.code@gmail.com'
EMAIL_PASSWORD = 'pnlr bdta shwz atpm'

def generate_reset_token(email):
    return serializer.dumps(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=600):
    try:
        email = serializer.loads(token , salt='password-reset-salt', max_age=expiration)
        return email
    except:
        return None

def send_email(receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)

        print(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Verify the token and extract the email
    email = verify_reset_token(token)
    if not email:
        return "The reset link is invalid or has expired. Please request a new one.", 400

    if request.method == 'POST':
        # Get the new password from the form
        new_password = request.form['password']

        # Update the user's password in the database
        collection.update_one({'email': email}, {'$set': {'password': new_password}})

        return redirect('/login')

        # return "Your password has been successfully reset. You can now log in.", 200

    # Render the reset password form
    return render_template('reset_password.html', email=email)


@app.route('/forgot', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        user = collection.find_one({'email': email})
        if user:
            token = generate_reset_token(email)
            send_email(email, 'Password Reset', f"Click the link to reset your password: http://192.168.156.235:2122/reset-password/{token}")
            return redirect('/login')
            # return 'Password reset link sent'
        else:
            return 'User not found'
    return render_template('forgotpassword.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{5,}$'
        if not re.match(password_regex, password):
            error = "Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character"
            return render_template('register.html', error=error)
        else:
            if password != confirm_password:
                error = "Passwords do not match"
                return render_template('register.html', error=error)
            user = collection.find_one({'email': email})
        if user:
            error = "User already exists"
            return render_template('register.html', error=error)
        collection.insert_one({'name': name, 'email': email, 'password': password, 'confirm_password': confirm_password})
        return redirect('/login')
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = collection.find_one({'email': email, 'password': password})
        error = "Invalid email or password"
        if user:
            session['user'] = email  # Store user email in session
            return redirect('/todos')
        return render_template('login.html', error=error)
    return render_template('login.html')

def login_required(func):
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect('/login')
        print(session['user'])
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Preserve the original function name
    return wrapper

@app.route('/goback')
def goback():
    return redirect('/todos')

@app.route('/todos', methods=['GET', 'POST'])
@login_required  # Protect this route
def todos():
    error = None  # Initialize error to None
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        
        # Validation: Check if title is at least 4 characters long
        if len(title) >= 3:
            todo = ToDo(title=title, desc=description)
            db.session.add(todo)
            db.session.commit()
            return redirect('/todos')  # Redirect to clear form data
        else:
            error = "Title must be at least 3 characters long"

    # Query all todos and pass error to the template
    alltodo = ToDo.query.all()
    return render_template('index.html', alltodo=alltodo, error=error)

@app.route('/delete/<int:sNo>')
@login_required  # Protect this route
def delete(sNo):
    todo = ToDo.query.filter_by(sNo=sNo).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect('/todos')

@app.route('/update/<int:sNo>', methods=['GET', 'POST'])
@login_required  # Protect this route
def update(sNo):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        todo = ToDo.query.filter_by(sNo=sNo).first()
        todo.title = title
        todo.desc = description
        db.session.add(todo)
        db.session.commit()
        return redirect('/todos')

    todo = ToDo.query.filter_by(sNo=sNo).first()
    return render_template('update.html', todo=todo)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=2122)
