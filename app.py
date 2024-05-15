from flask import Flask, request, render_template, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
import os

#Initialize app
app = Flask(__name__)
#Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Adminadmin123@localhost/usersdb'

#Initialize db
db = SQLAlchemy()
db.init_app(app)
migrate=Migrate(app, db)
 
basedir = os.path.abspath(os.path.dirname(__file__))
 
 
@app.route('/')
def index():
    return "Hello, world!"
 
# db = SQLAlchemy(app) creates an object of SQLAlchemy and stores it in a variable db.
ma = Marshmallow(app) # creates an object of Marshmallow and stores it in a variable ma.
 
#Users Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(50))
 
 
    def __init__(self, first_name, last_name, email, password, age, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.age = age
        self.gender = gender

#Users Schema
class UsersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        sqla_session = db.session
 
 
#Init Schema
users_schema = UsersSchema() #Users_schema will be used when dealing with users
 
#POST Endpoint
#Create User
@app.route('/user', methods=['POST'])
def add_user():
    new_user = users_schema.load(request.json)
    print(new_user)
    db.session.add(new_user)
    db.session.commit()
    return users_schema.jsonify(new_user)
 

#GET All Users - returns a list of current Users present in the database
@app.route('/all-users', methods=['GET'])
def get_users():
    all_users = Users.query.all()
    result = users_schema.dump(all_users, many=True)
    return jsonify(result)

 
#GET Single User - returns a single user with the specified ID in the database
@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    user = Users.query.get(id) #Select*from Users where id=id
    return users_schema.jsonify(user)

 
#Edit/Update a User - allows us for a PUT request and update the User with the specified ID in the database
@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = Users.query.get(id) #Select*from Users where id=id
    '''
    Update user
    set first_name = "",
    set last_name = "",
    set email = "",
    set password = "",
    set age = "",
    and setgender = ""
    where user_id = id
    '''
    user = users_schema.load(request.json, instance=user, partial=True)
    db.session.commit()
    return users_schema.jsonify(user)

 
#Delete User - allows us for a DELETE request deleting a User with the specified ID in the Database
@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    user = Users.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return users_schema.jsonify(user)
 
 
if __name__ == '__main__':
    app.run(debug=True)
   