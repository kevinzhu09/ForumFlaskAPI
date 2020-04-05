# Created by Kevin Zhu
# This file is the main file to run.
# create_table_example.sql provides an example case of what kind of table this API can work with.
# requirements.txt should be in the same folder as this file. It lists the dependencies to install for this application.
#
# Additional modules part of this API:
# users_table_SQL.py, which contains the SQL functions to work with the PostgreSQL database.
# db_config.json, which contains the sensitive configuration info to connect to the PostgreSQL database.
# mail_JWT_config.json, which contains the mail client and JWT configuration info.
# hash_code_functions.py, which contains the functions for storing the user password in a hash code.
# constants.py, which contains the constants including fields, which can be modified.
# These files should all be in the same folder.
# This app requires Python 3.7 or later.

# External modules: flask handles the URI routes for the API requests. It also allows JSON to be easily written.
# flask_jwt_extended handles the JSON Web Tokens (JWT) integration which is used for login verification.
# flask_mail handles the mail server.
# json helps for reading .json files.
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from routes.user_routes import user_routes, get_fields_from_request
from routes.post_routes import post_routes
from routes.routes_config import *

from routes.SQL_functions.users_table_SQL import *

from constants import APP_URI_LIST, APP_URI, MINUTES_BEFORE_TOKEN_EXPIRE, SERVER_NAME, TIME_TO_EXPIRE
from hash_code_functions import *
from flask import jsonify, render_template, request
from flask_jwt_extended import create_access_token
from flask_mail import Message, Mail

# Configuration for the Flask app, JWT integration and mail server:
basedir = path.abspath(path.dirname(__file__))

app = Flask(__name__, template_folder=path.join(basedir, '/templates'))

cors = CORS(app, resources={r"/api/*": {"origins": APP_URI_LIST}})

# with open(path.join(basedir, 'mail_JWT_config.json')) as file:
#     mail_JWT_data = load(file)

dirname = path.dirname(__file__)
mail_JWT_filename = path.join(dirname, 'config', 'mail_JWT_config.json')

with open(mail_JWT_filename) as file:
    mail_JWT_data = load(file)

app.config['JWT_SECRET_KEY'] = mail_JWT_data['JWT_SECRET_KEY']
app.config['MAIL_SERVER'] = mail_JWT_data['MAIL_SERVER']
app.config['MAIL_PORT'] = mail_JWT_data['MAIL_PORT']
app.config['MAIL_USERNAME'] = mail_JWT_data['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = mail_JWT_data['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = mail_JWT_data['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = mail_JWT_data['MAIL_USE_SSL']

jwt = JWTManager(app)
mail = Mail(app)

app.register_blueprint(user_routes)
app.register_blueprint(post_routes)


# If there are more types of errors, each error gets a code of 1,2,4,8,16, etc. The code is saved in a variable and
# added to for each error. If the code != 0, then a 409 error or some other error is returned. The recipient of this
# request can check with javascript or some language which errors happened. if the code is code=7=1110, then it can
# be checked with: code=7 && 1 | code && 2 | code && 4 | code && 8 | etc.
@app.route('/api/register', methods=['POST'])
def register():
    email = request_dynamic(request.is_json)('email')
    username = request_dynamic(request.is_json)('username')
    if email_exists(conn_info, email):
        if username_exists(conn_info, username):
            return jsonify(message='That email is taken. That username is also taken.', code=3), 409
        else:
            return jsonify(message='That email is taken.', code=1), 409
    elif username_exists(conn_info, username):
        return jsonify(message='That username is taken.', code=2), 409
    else:
        values_list = get_fields_from_request()
        password = request_dynamic(request.is_json)('password')
        hash_code = get_hash_code(password)
        unverified_user_id = insert_user(*values_list, conn=conn_info, hash_code=hash_code, email=email,
                                         username=username)

        access_token = create_access_token(
            identity={"email": email, "username": username, "unverified_user_id": unverified_user_id},
            expires_delta=TIME_TO_EXPIRE)
        verify_url = APP_URI + "/verify?token=" + access_token
        msg = Message(
            body="To verify your account, please click the following link. If you did not create an account with us "
                 "recently, disregard this email. This link expires after %d minutes.\n%s" % (
                     MINUTES_BEFORE_TOKEN_EXPIRE, verify_url),
            html=render_template('verification_email.html', url=verify_url,
                                 minutes=MINUTES_BEFORE_TOKEN_EXPIRE, username=username, server=SERVER_NAME),
            sender="no-reply@user-api.com",
            recipients=[email],
            subject="Account Verification Link for " + SERVER_NAME)
        mail.send(msg)

        return jsonify(message="User created successfully. Verification email sent to %s." % email, code=0), 201


@app.route('/api/password/reset', methods=['POST'])
def password_reset():
    email = request_dynamic(request.is_json)('email')
    if email_exists(conn_info, email):
        username = email.split("@")[0]
        access_token = create_access_token(identity={"email": email}, expires_delta=TIME_TO_EXPIRE)
        reset_url = APP_URI + "/password/reset/confirm?token=" + access_token
        msg = Message(
            body="To reset your password, please click the following link. If you did not request a password reset, "
                 "disregard this email. This link expires after %d minutes.\n%s" % (
                     MINUTES_BEFORE_TOKEN_EXPIRE, reset_url),
            html=render_template('password_reset_email.html', url=reset_url,
                                 minutes=MINUTES_BEFORE_TOKEN_EXPIRE, username=username, server=SERVER_NAME),
            sender="no-reply@user-api.com",
            recipients=[email],
            subject="Password Reset Link for " + SERVER_NAME)
        mail.send(msg)

        return jsonify(message="Email sent to %s." % email, code=0), 202
    else:
        return jsonify(message="Email not found.", code=1), 404


if __name__ == '__main__':
    app.run()
