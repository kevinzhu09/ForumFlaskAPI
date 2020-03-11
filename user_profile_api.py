# Created by Kevin Zhu
# This file is the main file to run.
# requirements.txt should be in the same folder as this file. It lists the dependencies to install for this application.
#
# Additional modules part of this API:
# SQL_commands.py, which contains the SQL functions to work with PostgreSQL and the pgAdmin database.
# db_config.json, which contains the sensitive configuration info to connect to PostgreSQL and the pgAdmin database.
# mail_JWT_config.json, which contains the mail client and JWT configuration info.
# hash_code_functions.py, which contains the functions for storing the user password in a hash code.
# constants.py, which contains the constants including fields, which can be modified in order to work with a variable
# number of desired fields/columns in the database.
# These files should all be in the same folder.
# This app requires Python 3.7 or later.

from hash_code_functions import *
from SQL_commands import *

# External modules: flask handles the URI routes for the API requests. It also allows JSON to be easily written.
# flask_jwt_extended handles the JSON Web Tokens (JWT) integration which is used for login verification.
# flask_mail handles the mail server.
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_mail import Mail, Message

from constants import DESIRED_FIELDS, HOST_URI, MINUTES_BEFORE_TOKEN_EXPIRE, TIME_TO_EXPIRE

# Configuration for the Flask app, JWT integration and mail server:
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

with open('mail_JWT_config.json') as file:
    mail_JWT_data = json.load(file)

app.config['JWT_SECRET_KEY'] = mail_JWT_data['JWT_SECRET_KEY']
app.config['MAIL_SERVER'] = mail_JWT_data['MAIL_SERVER']
app.config['MAIL_PORT'] = mail_JWT_data['MAIL_PORT']
app.config['MAIL_USERNAME'] = mail_JWT_data['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = mail_JWT_data['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = mail_JWT_data['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = mail_JWT_data['MAIL_USE_SSL']

jwt = JWTManager(app)
mail = Mail(app)

# With the information from db_config.json, configure the connection to PostgreSQL and the pgAdmin database.
# Returns the cursor object which can be used to run SQL commands.
cur = config()


# Helper function for the API. It allows the API to accept requests in either JSON or through form-data.
def request_dynamic(request_is_json, allow_null=False):
    if allow_null:
        if request_is_json:
            return lambda value: request.json.get(value)
        else:
            return lambda value: request.form.get(value)
    else:
        if request_is_json:
            return lambda value: request.json[value]
        else:
            return lambda value: request.form[value]


# Helper function that allows the API to accept a variable number of arguments.
def get_fields_from_request():
    return [request_dynamic(request.is_json, allow_null=True)(attribute) for attribute in DESIRED_FIELDS]


@app.route('/register', methods=['POST'])
def register():
    email = request_dynamic(request.is_json)('email')
    if email_exists(cur, email):
        return jsonify(message='That email already exists.'), 409
    else:
        values_list = get_fields_from_request()
        password = request_dynamic(request.is_json)('password')
        hash_code = get_hash_code(password)
        create_user(*values_list, cur=cur, hash_code=hash_code, email=email)
        return jsonify(message="User created successfully."), 201


@app.route('/login', methods=['POST'])
def login():
    email = request_dynamic(request.is_json)('email')
    password = request_dynamic(request.is_json)('password')

    hash_code = query_hash_code(cur, email)
    verify = verify_hash_code(password, hash_code)
    if verify:
        access_token = create_access_token(identity=email, expires_delta=TIME_TO_EXPIRE)
        return jsonify(message="Login succeeded! Access token returned.", access_token=access_token)
    else:
        return jsonify(message="Invalid email or password."), 401


@app.route('/users', methods=['PUT'])
@jwt_required
def update_user():
    email = request_dynamic(request.is_json)('email')
    if email_exists(cur, email):
        values_list = get_fields_from_request()

        modify_user(*values_list, cur=cur, email=email)
        return jsonify(message="You updated a user.")
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users', methods=['DELETE'])
@jwt_required
def remove_user():
    email = request_dynamic(request.is_json)('email')
    if email_exists(cur, email):
        delete_user(cur, email)
        return jsonify(message="You deleted a user.")
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users/<int:user_id>', methods=["GET"])
@jwt_required
def user_details_by_id(user_id: int):
    user = select_one_user(cur, 'user_id', user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users', methods=["GET"])
@jwt_required
def user_details():
    email = request.args.get('email')
    if email:
        user = select_one_user(cur, 'email', email)
        if user:
            return jsonify(user)
        else:
            return jsonify(message="That user does not exist."), 404
    else:
        users_list = select_all_users(cur)
        if users_list:
            return jsonify(users_list)
        else:
            return jsonify(message="There are no users.")


@app.route('/password/reset', methods=['POST'])
def password_reset():
    email = request_dynamic(request.is_json)('email')
    if email_exists(cur, email):
        access_token = create_access_token(identity=email, expires_delta=TIME_TO_EXPIRE)
        reset_url = HOST_URI + "/password/reset/confirm?token=" + access_token
        msg = Message(
            body="To reset your password, please click the following link. If you did not request a password reset, "
                 "disregard this email. This link expires after %d minutes. %s" % (MINUTES_BEFORE_TOKEN_EXPIRE,
                                                                                   reset_url),
            sender="no-reply@user-api.com",
            recipients=[email],
            subject="Password Reset Link for Kevin's Database")
        mail.send(msg)

    return jsonify(message="Email sent to %s." % email), 202


@app.route('/password/reset/confirm/', methods=['GET'])
def password_reset_confirm():
    return send_from_directory(directory='static', filename='password_reset_confirm.html')


@app.route('/password', methods=['PUT'])
@jwt_required
def change_password():
    email = get_jwt_identity()
    if email_exists(cur, email):
        password = request_dynamic(request.is_json)('password')
        hash_code = get_hash_code(password)
        modify_hash_code(cur, hash_code, email)
        return jsonify(message="Password changed successfully.")
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/not_found')
def not_found():
    return jsonify(message='That resource was not found.'), 404


if __name__ == '__main__':
    app.run()
