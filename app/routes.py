from flask import request, render_template
from . import app, db
from .models import Task


#create main route 
@app.route('/')
def index():
    return "Welcome to the index page"
# create 2 routes using @app.route

# [GET] all tasks - Return all of the tasks in the tasks_list
#define route 
@app.route('/tasks')
def get_tasks():
    #get tasks from storage (fake data)
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    # get the posts from the database
    tasks = db.session.execute(select_stmt).scalars().all()
    return [t.to_dict() for t in tasks]


# [GET] a single task by ID - Get a single task from a task id. Should return a 404 error if the task with that ID does not exist.
@app.route('/tasks/<int:task_id>')
def get_task(task_id):
    #grab tasks from storage
    task = db.session.get(Task, task_id)
    #for each dict in the list of tasks dicts
    if task:
        #If the key of ID matches task
        return task.to_dict()
            # return that post dict
    else:
        # if we loop through and task doesnt exist, create error message
        return {'error': f"Task with an ID of {task_id} does not exist"}, 404
    
#     Continue working on your Flask Tasks API. Add a new route for creating a new task. It should be a POST request to /tasks. 
# - Follow same steps that we used for creating Post and User today - make sure its JSON, make sure you have all required fields

# The following fields are required:
# title
# description
# You can also add an optional dueDate field. *BONUS*

# On creation, it should create a new task with the following:
# id
# title
# description
# completed
# createdAt
# dueDate *optional
# Once the route is completed, set up a database with a task table using Flask-SQLAlchemy and Flask-Migrate.

# Steps:
# pip install flask-sqlalchemy flask-migrate
# In the __init__.py, instantiate SQLAlchemy (db = SQLAlchemy(app)) and Migrate (migrate = Migrate(app, db))
# Set up the config file with SQLALCHEMY_DATABASE_URI
# Create models.py with a class Task(db.Model) *don't forget to import models into __init__.py
# Add the columns
# Set up the migrations folder - flask db init
# Create the first migration - flask db migrate -m "YOUR MESSAGE HERE"
# Apply the migration to the database - flask db upgrade
    
@app.route('/tasks', methods=['POST'])
def create_task():
    #check to see if request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # get the data from the request body
    data = request.json
    # validate the incoming data
    required_fields = ['title', 'description']
    missing_fields = []
    # for each of the required fields
    for field in required_fields:
        # if field not in request body dict
        if field not in data:
            # add the field to the list of missing fields
            missing_fields.append(field)
    # if  there are any missing fields, send back an error with 400 status code
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # get data values
    title = data.get('title')
    description = data.get('description')
    

    # create new task instance with data
    new_task = Task(title=title, description=description)

    # return the newly created task dict with a 201 created status code
    return new_task.to_dict(), 201