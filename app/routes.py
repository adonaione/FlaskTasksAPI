from flask import Flask, request, render_template
from . import app, db
from .models import Task, User
from .auth import basic_auth, token_auth

#create main route 
@app.route('/')
def index():
    return render_template('index.html')
# create 2 routes using @app.route

#CREATE USER ENDPOINTS
#sample user 
#   "full_name": "Adonai Romero",
#   "username": "adonair",
#   "email": "adonai.devs@gmail.com",
#   "password": "abc123"
#create new user
@app.route('/users', methods=['POST'])
def create_user():
    #check to make sure that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # get the data from the request body
    data = request.json

    # validate that the data has all of the required fields
    required_fields = ['full_name', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body."}, 400
    # Pull the individual data from the body
    full_name = data.get('full_name')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check to see if the provided username and/or email already exists
    check_users = db.session.execute(db.select(User).where((User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': 'A user with that username and/or email already exists'}, 400
    
    # create a new instance of a user with the data from the request
    new_user = User(full_name=full_name, username=username, email=email, password=password)

    return new_user.to_dict(), 201

#Login to get a token
@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return {
        'token': token,
        'tokenExpiration': user.token_expiration
    }

@app.route('/users')
def get_users():
    select_stmt = db.select(User)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(User.full_name.ilike(f"%{search}%"))
    users = db.session.execute(select_stmt).scalars().all()
    return [u.to_dict() for u in users]
# [GET] all tasks - Return all of the tasks in the tasks_list
#define route 
@app.route('/tasks')
def get_tasks():
    #get tasks from storage (fake data)
    select_stmt = db.select(Task)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Task.title.ilike(f"%{search}%"))
    # get the tasks from the database
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
            # return that tasks dict
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
@token_auth.login_required
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

    # get the logged in user
    current_user = token_auth.current_user()
    

    # create new task instance with data
    new_task = Task(title=title, description=description, user_id=current_user.id)

    # return the newly created task dict with a 201 created status code
    return new_task.to_dict(), 201

## CREATE "UD" or CRUD and add User routes

# update task route
@app.route('/tasks/<int:task_id>', methods=['PUT'])
@token_auth.login_required
def edit_task(task_id):
    #check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    #Lets the user find task in db
    task = db.session.get(Task, task_id)
    if task is None:
        return {'error': f"Task with an ID #{task_id} does not exist"}, 404
    #get the current user based on token
    current_user = token_auth.current_user()
    #check if the current user is the author
    if current_user is not task.author:
        return {'error': "This is not your task. You do not have permission to edit"}, 403
    #Get the data from the request
    data = request.json
    #Pass that data into the task's update method
    task.update(**data)
    return task.to_dict()

#Delete a Task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@token_auth.login_required
def delete_task(task_id):
    #Deletes a task given its id
    #based on the task_id parameter, check to see if task exists
    task  = db.session.get(Task, task_id)

    if task is None:
        return {'error': f'Task with {task_id} does not exist. Please try again.'}, 404

    ##make sure this is the user that created the task
    current_user = token_auth.current_user()
    if task.author != current_user:
        return {'error': 'You do not have permission to delete this task.'}, 403
    # delete task
    task.delete()
    return {'success': f"{task.title} was successfully deleted."}


# Get a user
@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        return user.to_dict()
    else:
        return {'error': f"User with {user_id} does not exist"}, 404
    
# Update a user
@app.route('/users/<int:user_id>', methods=['PUT'])
@token_auth.login_required
def edit_user(user_id):
    # Check to see that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the user based on the user id
    user = db.session.get(User, user_id)
    # check if user exists
    if user is None:
        return {'error': f"User with  {user_id} does not exist."}, 404
    
    # Get the logged in user based on the token
    current_user = token_auth.current_user()
    # Check if the user to edit is the logged in user
    if user is not current_user:
        return {'error': 'You do not have permission to edit this user'}, 403
    
    data = request.json
    user.update(**data)
    return user.to_dict()


# delete a user
@app.route('/users/<int:user_id>', methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    # Get the user based on the user_id
    user = db.session.get(User, user_id)
    # Chekc if the user exists
    if user is None:
        return {'error': f"User with {user_id} does not exist"}, 404
    # get the logged in user based on the token
    current_user = token_auth.current_user()
    # check if the user to edit is the logged in user
    if user is not current_user:
        return {'error': 'You do not have permission to delete this user'}, 403
    # Delete the user
    user.delete()
    return {'success': f"{user.username} has been deleted."}, 200



