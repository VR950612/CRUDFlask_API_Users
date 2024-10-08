from flask import Flask, request, render_template, jsonify, Response, make_response
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import os


#Initialize app
app = Flask(__name__)
#Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
if 'RDS_DB_NAME' in os.environ:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username=os.environ['RDS_USERNAME'],
        password=os.environ['RDS_PASSWORD'],
        host=os.environ['RDS_HOSTNAME'],
        port=os.environ['RDS_PORT'],
        database=os.environ['RDS_DB_NAME'],
    )
else:
    # our database uri
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Adminadmin123@localhost/usersdb'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Adminadmin123@localhost/merchantdb'

# Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
    username='postgres',
    password='12345678',
    host='localhost',
    port='5432',
    database='usersdb'
)

    app.config['SQLALCHEMY_BINDS'] = {
    'merchants': 'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
        username='postgres',
        password='12345678',
        host='localhost',
        port='5432',
        database='usersdb'
    )
}

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

    received_data = request.json
    print(received_data)
    received_email = received_data['email']
    print(received_email)

    #Code to prevent adding users with duplicate email addresses
    #Check if the received email matches any record in the database
    user = Users.query.filter_by(email=received_email).first()
    #if user exists, then its a failure, return a 200 status code with a duplicate email found message
    if user:
        return make_response({"message": "User with this email exists, please try again"}, 200, {'Content-Type': 'application/json'})
    # else - if user does not exist, then add the new user to database, return a 201 status code with success message
    else:
        db.session.add(new_user)
        db.session.commit()        
        return make_response({"message": "User added successfully"}, 201, {'Content-Type': 'application/json'})        

    #return users_schema.jsonify(new_user)

#POST Endpoint
#Login for user
@app.route('/login', methods=['POST'])
def login(): 
    received_login_info = request.json
    print(received_login_info)
    received_email = received_login_info['email']
    received_password = received_login_info['password']

    #Check if the received email and password match any record in the database
    user = Users.query.filter_by(email=received_email, password=received_password).first()

    #if user exists, then its a success, return a 201 status code with a success message
    if user:
        return make_response(users_schema.jsonify(user), 201, {'Content-Type': 'application/json'})
    # else - if user does not exist, then return a 404 status code with an invalid email or password message
    else:
        return make_response({"message": "Invalid username or password"}, 404, {'Content-Type': 'application/json'})
 

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


#Merchant Model
class Merchants(db.Model):
    __tablename__ = 'merchants'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
   
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
      
#Merchants Schema
class MerchantsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Merchants
        load_instance = True
        sqla_session = db.session
 
 
#Init Schema
merchants_schema = MerchantsSchema() #Merchants_schema will be used when dealing with admin
 
#POST Endpoint
#Create Merchant
@app.route('/merchant', methods=['POST'])
def add_merchant():
    new_merchant = merchants_schema.load(request.json)
    print(new_merchant)

    received_data = request.json
    print(received_data)
    received_email = received_data['email']
    print(received_email)

    #Code to prevent adding admin with duplicate email addresses
    #Check if the received email matches any record in the database
    merchant = Merchants.query.filter_by(email=received_email).first()
    #if admin exists, then its a failure, return a 200 status code with a duplicate email found message
    if merchant:
        return make_response({"message": "Admin with this email exists, please try again"}, 200, {'Content-Type': 'application/json'})
    # else - if admin does not exist, then add the new admin to database, return a 201 status code with success message
    else:
        db.session.add(new_merchant)
        db.session.commit()        
        return make_response({"message": "Admin added successfully"}, 201, {'Content-Type': 'application/json'})        

    #return merchant_schema.jsonify(new_merchant)

#POST Endpoint
#Login for Merchant
@app.route('/merchant_login', methods=['POST'])
def merchant_login(): 
    received_merchant_login_info = request.json
    print(received_merchant_login_info)
    received_email = received_merchant_login_info['email']
    received_password = received_merchant_login_info['password']

    #Check if the received email and password match any record in the database
    merchant = Merchants.query.filter_by(email=received_email, password=received_password).first()

    #if admin exists, then its a success, return a 201 status code with a success message
    if merchant:
        return make_response(merchants_schema.jsonify(merchant), 201, {'Content-Type': 'application/json'})
    # else - if admin does not exist, then return a 404 status code with an invalid email or password message
    else:
        return make_response({"message": "Invalid username or password"}, 404, {'Content-Type': 'application/json'})
 
 
#GET All Merchants - returns a list of current Merchants present in the database
@app.route('/all-merchants', methods=['GET'])
def get_merchants():
    all_merchants = Merchants.query.all()
    result = merchants_schema.dump(all_merchants, many=True)
    return jsonify(result)

 
#GET Single Merchant - returns a single merchant with the specified ID in the database
@app.route('/merchant/<id>', methods=['GET'])
def get_merchant(id):
    merchant = Merchants.query.get(id) #Select*from Merchant where id=id
    return merchants_schema.jsonify(merchant)

 
#Edit/Update a Merchant - allows us for a PUT request and update the Merchant with the specified ID in the database
@app.route('/merchant/<id>', methods=['PUT'])
def update_merchant(id):
    merchant = Merchants.query.get(id) #Select*from Merchant where id=id
    '''
    Update merchant
    set first_name = "",
    set last_name = "",
    set email = "",
    set password = "",
    where merchant_id = id
    '''
    merchant = merchants_schema.load(request.json, instance=merchant, partial=True)
    db.session.commit()
    return merchants_schema.jsonify(merchant)

 
#Delete Merchant - allows us for a DELETE request deleting a Merchant with the specified ID in the Database
@app.route('/merchant/<id>', methods=['DELETE'])
def delete_merchant(id):
    merchant = Merchants.query.get(id)
    db.session.delete(merchant)
    db.session.commit()
    return merchants_schema.jsonify(merchant)


if __name__ == "__main__":
    app.run(port=5004, debug=True)
