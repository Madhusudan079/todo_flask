from flask import  *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config.db_email_config import *
from config.sentry_intergration import *
from flasgger import Swagger
from itsdangerous import URLSafeTimedSerializer
from werkzeug.exceptions import HTTPException
import random
from werkzeug.utils import secure_filename
from utils.auth import hash_password, verify_password
import re
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix



a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

SECRET_KEY = ''.join(random.choices(a, k=16))
serializer = URLSafeTimedSerializer(SECRET_KEY)

# config = {
#     "DEBUG": True,          # some Flask specific configs
#     "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
#     "CACHE_DEFAULT_TIMEOUT": 300
# }

app = Flask(__name__)
swagger = Swagger(app)
# app.config.from_mapping(config)
# cache = Cache(app)
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'super secret key'

db = SQLAlchemy(app)

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

allowed_image_extension = ['jpg', 'png', 'jpeg']

# Define the ToDo model
class ToDo(db.Model):
    sNo = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now().replace(microsecond=0))    
    file = db.Column(db.String(200), nullable=True)
    user_id = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"{self.sNo} - {self.title} - {self.desc} - {self.file} -{self.user_id}"
    

# Create the database tables
with app.app_context():
    db.create_all()

def generate_reset_token(email):
    return serializer.dumpsss(email, salt='password-reset-salt')

def verify_reset_token(token, expiration=600):
    try:
        email = serializer.loads(token , salt='password-reset-salt', max_age=expiration)
        return email
    except:
        return None
    
def allow_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_image_extension

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
# @Cache.cached(timeout=600)
def reset_password(token):
    # Verify the token and extract the email
    email = verify_reset_token(token)
    if not email:
        return "The reset link is invalid or has expired. Please request a new one.", 400

    if request.method == 'POST':
        # Get the new password from the form
        new_password = request.form['password']

        # Update the user's password in the database
        collection.update_one({'email': email}, {'$set': {'password': hash_password(new_password)}})
        flash('Your password has been successfully reset. You can now log in.', 'success')
        return redirect('/login')

        # return "Your password has been successfully reset. You can now log in.", 200

    # Render the reset password form
    return render_template('reset_password.html', email=email)


@app.route('/forgot', methods=['GET', 'POST'])
def forgotpassword():
    if request.method == 'POST':
        email = request.form['email']
        print(email)
        user = collection.find_one({'email': email})
        if user:
            token = generate_reset_token(email)
            send_email(email, 'Password Reset', f"Click the link to reset your password: https://t31kp2fr-7777.inc1.devtunnels.ms/reset-password/{token}")
            flash('password reset link send to your email', 'success')
            return redirect('/login')
            # return 'Password reset link sent'
        else:
            return render_template('forgotpassword.html', error="User not found.")
    return render_template('forgotpassword.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        if not name or name.isdigit():
            flash("Name must be a valid string (not numeric or empty).", 'error')
            return render_template('register.html')

        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$'
        if not re.match(password_regex, password):
            flash("Password must be at least 6 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.", 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')

        # Check if user already exists
        user = collection.find_one({'email': email})
        if user:
            flash('User already exists', 'error')
            return render_template('register.html')
        
        # Hash the password and save the user
        hashed_password = hash_password(password)
        collection.insert_one({'name': name, 'email': email, 'password': hashed_password, 'confirm_password': confirm_password})
        flash('User registered successfully', 'success')
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session['email'] = email 
        
        # Check if user exists
        user = collection.find_one({'email': email})
        if not user:
            flash('User not found', 'error')
            return render_template('login.html')
        
        # Check if password is correct  
        if user and verify_password(user['password'], password):
            print(verify_password)
            session['user'] = email
            flash('Logged in successfully', 'success')
            return redirect('/todos/1')
        
        flash("Invalid email or password", 'error')
        return render_template('login.html')
    
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
    return redirect('/todos/1')

@app.route('/home_page')
@login_required
def home_page():
    return render_template('home.html')

@app.route('/todos/<int:page>', methods=['GET', 'POST'])
@login_required
def todos(page=1):
    error = None
    todos_per_page = 10
    search_query = request.args.get('search', '').strip()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        file_upload = request.files['file']

        if len(title) < 3:
            flash("Title must be at least 3 characters long", 'error')
        else:
            if file_upload and file_upload.filename != '':
                if not allow_image(file_upload.filename):
                    flash('Invalid file type. Please upload file of type {}.'.format(allowed_image_extension), 'error')
                    return redirect(url_for('todos', page=page))
                filename = secure_filename(file_upload.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_upload.save(file_path)
            else:
                filename = None

            todo = ToDo(title=title, desc=description, file=filename, user_id=session['user'])
            db.session.add(todo)
            db.session.commit()
            flash('Todo added successfully', 'success')
            return redirect(url_for('todos', page=page))

    if search_query:
        todos = ToDo.query.filter(ToDo.title.contains(search_query) | ToDo.desc.contains(search_query), ToDo.user_id == session['user']).paginate(page=page, per_page=todos_per_page)
        alltodo = todos.items
        has_previous = todos.has_prev
        has_next = todos.has_next
        search_performed = True
        flash(f'Search Successfully', 'success')
    else:
        pagination = ToDo.query.filter(ToDo.user_id == session['user']).paginate(page=page, per_page=todos_per_page)
        alltodo = pagination.items
        has_previous = pagination.has_prev
        has_next = pagination.has_next
        search_performed = False

    return render_template(
        'index.html',
        email=session.get('email'),
        alltodo=alltodo,
        error=error,
        page=page,
        todos_per_page=todos_per_page,
        has_previous=has_previous,
        has_next=has_next,
        search_performed=search_performed,
        search_query=search_query
    )



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/delete/<int:sNo>')
@login_required  # Protect this route
def delete(sNo):
    todo = ToDo.query.filter_by(sNo=sNo).first()

    if not todo:
        flash('Todo not found', 'error')
        return redirect(url_for('todos', page=1))  # Redirect safely

    if todo.file:  # Ensure file exists before using it
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], todo.file)
        
        if os.path.exists(file_path):  # Check if file_path is valid
            os.remove(file_path)

    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted successfully', 'success')

    return redirect(url_for('todos', page=1))

@app.route('/update/<int:sNo>', methods=['GET', 'POST'])
@login_required  # Protect this route
def update(sNo):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        file_upload = request.files['file']
        todo = ToDo.query.filter_by(sNo=sNo).first()
        todo.title = title
        todo.desc = description

        old_file = todo.file

        if file_upload and file_upload.filename != '':
            if not allow_image(file_upload.filename):
                flash('Invalid file type. Please upload file of type {}.'.format(allowed_image_extension), 'error')
                return redirect(url_for('update', sNo=sNo))
            filename = secure_filename(file_upload.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            if old_file:
                old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_file)
                print(old_file_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            file_upload.save(file_path)
            todo.file = filename


        db.session.add(todo)
        db.session.commit()
        flash('todo update successfully', 'success')
        return redirect('/todos/1')

    todo = ToDo.query.filter_by(sNo=sNo).first()
    return render_template('update.html', todo=todo)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port = 7878)