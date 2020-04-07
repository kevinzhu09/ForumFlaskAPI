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
# APIConfig.json, which contains the constants including fields, which can be modified.
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

from hash_code_functions import *
from flask import jsonify, render_template, request
from flask_jwt_extended import create_access_token
from flask_mail import Message, Mail

from config.APIConfig import mail_data, JWT_data, APP_URI, TOKEN_TTL_TIMEDELTA, TOKEN_TTL_MINUTES, SERVER_NAME, SERVER_EMAIL

# Configuration for the Flask app, JWT integration and mail server:
basedir = path.abspath(path.dirname(__file__))

app = Flask(__name__, template_folder=path.join(basedir, '/templates'))

cors = CORS(app, resources={r"/api/*": {"origins": APP_URI}})

# with open(path.join(basedir, 'mail_JWT_config.json')) as file:
#     mail_JWT_data = load(file)


app.config['JWT_SECRET_KEY'] = JWT_data['JWT_SECRET_KEY']
app.config['MAIL_SERVER'] = mail_data['MAIL_SERVER']
app.config['MAIL_PORT'] = mail_data['MAIL_PORT']
app.config['MAIL_USERNAME'] = mail_data['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = mail_data['MAIL_PASSWORD']
app.config['MAIL_USE_TLS'] = mail_data['MAIL_USE_TLS']
app.config['MAIL_USE_SSL'] = mail_data['MAIL_USE_SSL']

jwt = JWTManager(app)
mail = Mail(app)

app.register_blueprint(user_routes)
app.register_blueprint(post_routes)


def send_email(access_token, email, username, email_type):
    if email_type == 'verification':
        url_path = "/verify"
        body_text = "To verify your account, please click the following link. If you did not create an account with " \
                    "us recently, disregard this email. "
        template = 'verification_email.html'
        subject = "Account Verification Link for " + SERVER_NAME
    elif email_type == 'reset':
        url_path = "/password/reset/confirm"
        body_text = "To reset your password, please click the following link. If you did not request a password " \
                    "reset, disregard this email. "
        template = 'password_reset_email.html'
        subject = "Password Reset Link for " + SERVER_NAME
    else:
        raise TypeError("Must include the email_type.")
    url = APP_URI + "%s?token=" % url_path + access_token
    body = "%s This link expires after %d minutes.\n%s" % (body_text, TOKEN_TTL_MINUTES, url)
    html = render_template(template, url=url, minutes=TOKEN_TTL_MINUTES, username=username, server=SERVER_NAME)
    msg = Message(body=body, html=html, sender=SERVER_EMAIL, recipients=[email], subject=subject)
    mail.send(msg)


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
            expires_delta=TOKEN_TTL_TIMEDELTA)
        send_email(access_token, email, username, 'verification')

        return jsonify(message="User created successfully. Verification email sent to %s." % email, code=0), 201


@app.route('/api/password/reset', methods=['POST'])
def password_reset():
    email = request_dynamic(request.is_json)('email')
    if email_exists(conn_info, email):
        username = email.split("@")[0]
        access_token = create_access_token(identity={"email": email}, expires_delta=TOKEN_TTL_TIMEDELTA)
        send_email(access_token, email, username, 'reset')

        return jsonify(message="Email sent to %s." % email, code=0), 202
    else:
        return jsonify(message="Email not found.", code=1), 404


if __name__ == '__main__':
    app.run()
