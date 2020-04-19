from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from routes.user_routes import user_routes
from routes.post_routes import post_routes
from routes.google_routes import google_routes
from routes.routes_config import request_dynamic

from routes.data_access.users_data_access import email_exists, username_exists, insert_regular_user

from hash_code_functions import get_hash_code
from flask import jsonify, render_template, request
from flask_jwt_extended import create_access_token
from flask_mail import Message, Mail
from os import path

from config.APIConfig import mail_data, JWT_data, APP_URI, TOKEN_TTL_TIMEDELTA, TOKEN_TTL_MINUTES, SERVER_NAME, \
    SERVER_EMAIL

basedir = path.abspath(path.dirname(__file__))

app = Flask(__name__, template_folder=path.join(basedir, '/templates'))

cors = CORS(app, resources={r"/api/*": {"origins": APP_URI}})


app.config['JWT_SECRET_KEY'] = JWT_data['JWT_SECRET_KEY']
app.config['SECRET_KEY'] = JWT_data['JWT_SECRET_KEY']
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
app.register_blueprint(google_routes)


# Using the expired_token_loader decorator, we will now call
# this function whenever an expired but otherwise valid access
# token attempts to access an endpoint
@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type),
        'code': 'expired'
    }), 401


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
    if email_exists(email, False):
        if username_exists(username, False):
            return jsonify(message='That email is taken. That username is also taken.', code=3), 409
        else:
            return jsonify(message='That email is taken.', code=1), 409
    elif username_exists(username, False):
        return jsonify(message='That username is taken.', code=2), 409
    else:
        password = request_dynamic(request.is_json)('password')
        hash_code = get_hash_code(password)
        unverified_user_id = insert_regular_user(hash_code=hash_code, email=email, username=username)

        access_token = create_access_token(
            identity={"email": email, "username": username, "unverified_user_id": unverified_user_id},
            expires_delta=TOKEN_TTL_TIMEDELTA)
        send_email(access_token, email, username, 'verification')

        return jsonify(message="User created successfully. Verification email sent to %s." % email, code=0), 201


@app.route('/api/password/reset', methods=['POST'])
def password_reset():
    email = request_dynamic(request.is_json)('email')
    if email_exists(email, False):
        username = email.split("@")[0]
        access_token = create_access_token(identity={"email": email}, expires_delta=TOKEN_TTL_TIMEDELTA)
        send_email(access_token, email, username, 'reset')

        return jsonify(message="Email sent to %s." % email, code=0), 202
    else:
        return jsonify(message="Email not found.", code=1), 404


if __name__ == '__main__':
    app.run()
