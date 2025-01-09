from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Avoids warnings
db = SQLAlchemy(app)

# Define the ToDo model
class ToDo(db.Model):
    sNo = db.Column(db.Integer, primary_key=True)  # Auto-incrementing primary key
    title = db.Column(db.String(200), nullable=False)  # Title field
    desc = db.Column(db.String(500), nullable=False)  # Description field
    date_created = db.Column(db.DateTime, default=datetime.now)  # Timestamp

    def __repr__(self):
        return f"{self.sNo} - {self.title}"

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()

# Home route to display and add todos
@app.route('/', methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        # Retrieve form data
        title = request.form['title']
        description = request.form['desc']
        todo = ToDo(title=title, desc=description)
        db.session.add(todo)
        db.session.commit()
        return redirect('/')  # Redirect to avoid resubmission on refresh

    # Query all ToDo items
    alltodo = ToDo.query.all()
    return render_template('index.html', alltodo=alltodo)

@app.route('/static/sourav.txt')
def sourav():
    return app.send_static_file('sourav.txt')

# Route to delete a ToDo item
@app.route('/delete/<int:sNo>')
def delete(sNo):
    todo = ToDo.query.filter_by(sNo=sNo).first()  # Find the item by sNo
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/update/<int:sNo>', methods=['GET', 'POST'])
def update(sNo):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['desc']
        todo = ToDo.query.filter_by(sNo=sNo).first()  # Find the item by sNo
        todo.title = title
        todo.desc = description
        db.session.add(todo)
        db.session.commit()
        return redirect('/')

    todo = ToDo.query.filter_by(sNo=sNo).first()  # Find the item by sNo
    return render_template('update.html', todo=todo)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
