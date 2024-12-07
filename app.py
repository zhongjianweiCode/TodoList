from flask import Flask, render_template, request, redirect
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from waitress import server

app = Flask(__name__)
Scss(app)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# initialize the app with the extension
db = SQLAlchemy(app)

# Data class ~ Row of data
class MyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self): 
        return f'<Task {self.id} {self.content}>'


with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    # add the task
    if request.method == 'POST':
        current_task = request.form.get('content')
        new_task = MyTask(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f'An error occurred: {e}')
            return f"An error occurred: {e}"
    elif request.method == 'GET':
        # fetch all tasks
        tasks = MyTask.query.order_by('created_at').all()
        return render_template('index.html', tasks=tasks)
    
# delete tasks
@app.route('/delete/<int:id>')
def delete(id: int):
    task_to_delete = MyTask.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        print(f'An error occurred: {e}')
        return f"An error occurred: {e}"
    
# update tasks
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id: int):
    task_to_update = MyTask.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form.get('content')
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(f'An error occurred: {e}')
            return f"An error occurred: {e}"
    elif request.method == 'GET':
        return render_template('update.html', task=task_to_update)

if __name__ == '__main__':    
    server(app, host="0,0,0,0", port=8080)