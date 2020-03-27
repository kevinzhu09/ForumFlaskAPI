from config.app_config import *
from SQL_functions.users_table_SQL import *

from constants import APP_URI, MINUTES_BEFORE_TOKEN_EXPIRE, SERVER_NAME, TIME_TO_EXPIRE, DESIRED_FIELDS
from hash_code_functions import *
from flask import jsonify, send_from_directory, render_template
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from flask_mail import Message


# Helper function that allows the API to accept a variable number of arguments.
def get_fields_from_request():
    return [request_dynamic(request.is_json, allow_null=True)(attribute) for attribute in DESIRED_FIELDS]


# If there are more types of errors, each error gets a code of 1,2,4,8,16, etc. The code is saved in a variable and
# added to for each error. If the code != 0, then a 409 error or some other error is returned. The recipient of this
# request can check with javascript or some language which errors happened. if the code is code=7=1110, then it can
# be checked with: code=7 && 1 | code && 2 | code && 4 | code && 8 | etc.
@app.route('/register', methods=['POST'])
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
        insert_user(*values_list, conn_info=conn_info, hash_code=hash_code, email=email, username=username)

        access_token = create_access_token(identity={"email": email}, expires_delta=TIME_TO_EXPIRE)
        reset_url = APP_URI + "/verify?token=" + access_token
        msg = Message(
            body="To verify your account, please click the following link. If you did not create an account with us "
                 "recently, disregard this email. This link expires after %d minutes.\n%s" % (
                     MINUTES_BEFORE_TOKEN_EXPIRE, reset_url),
            html=render_template('verification_email.html', url=reset_url,
                                 minutes=MINUTES_BEFORE_TOKEN_EXPIRE, username=username, server=SERVER_NAME),
            sender="no-reply@user-api.com",
            recipients=[email],
            subject="Account Verification Link for " + SERVER_NAME)
        mail.send(msg)

        return jsonify(message="User created successfully. Verification email sent to %s." % email, code=0), 201


@app.route('/verify', methods=['PUT'])
@jwt_required
def verify_account():
    email = get_jwt_identity().get("email")
    if email:
        password = request_dynamic(request.is_json)('password')
        hash_code = get_hash_code(password)
        if verify_hash_code(password, select_hash_code_from_unverified(conn_info, email)):

            rows_affected = verify_user(conn_info, email)
            if rows_affected == 1:
                return jsonify(message="User verified successfully.", code=0)
            else:
                # debugging:
                print(email)
                print(password)
                print(rows_affected)
                return jsonify(message="That user is verified, does not exist or is not the requester, or some other issue.", code=1), 404
        else:
            return jsonify(message="Unauthorized request to verify account. The password is wrong.", code=2), 401
    else:
        return jsonify(message="Unauthorized request to verify account.", code=4), 401


@app.route('/login', methods=['POST'])
def login():
    email = request_dynamic(request.is_json)('email')
    password = request_dynamic(request.is_json)('password')

    hash_code_and_id = select_hash_code_and_id(conn_info, email)
    if hash_code_and_id:
        hash_code = hash_code_and_id[0]
        verify = verify_hash_code(password, hash_code)
        if verify:
            user_id = hash_code_and_id[1]
            access_token = create_access_token(identity={"user_id": user_id}, expires_delta=TIME_TO_EXPIRE)
            return jsonify(message="Login succeeded! Access token returned.", access_token=access_token)
        else:
            return jsonify(message="Invalid email or password."), 401
    else:
        return jsonify(message="That email was not found."), 404


@app.route('/users', methods=['PUT'])
@jwt_required
def modify_user():
    user_id = get_jwt_identity().get("user_id")
    values_list = get_fields_from_request()
    rows_affected = update_user(*values_list, conn_info=conn_info, user_id=user_id)
    if rows_affected == 1:
        return jsonify(message="You updated a user.")
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users', methods=['DELETE'])
@jwt_required
def remove_user():
    user_id = get_jwt_identity().get("user_id")
    rows_affected = delete_user(conn_info, user_id)
    if rows_affected == 1:
        return jsonify(message="You deleted a user.")
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users/<int:user_id>', methods=["GET"])
@jwt_required
def user_details_by_id(user_id: int):
    user = select_one_user(conn_info, 'user_id', user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/users', methods=["GET"])
@jwt_required
def user_details():
    email = request.args.get('email')
    if email:
        user = select_one_user(conn_info, 'email', email)
        if user:
            return jsonify(user)
        else:
            return jsonify(message="That user does not exist."), 404
    else:
        users_list = select_all_users(conn_info)
        if users_list:
            return jsonify(users_list)
        else:
            return jsonify(message="There are no users.")


@app.route('/password/reset', methods=['POST'])
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

    return jsonify(message="Email sent to %s." % email), 202


@app.route('/password/reset/confirm/', methods=['GET'])
def password_reset_confirm():
    return send_from_directory(directory='static', filename='password_reset_confirm.html')


@app.route('/password', methods=['PUT'])
@jwt_required
def change_password():
    identity = get_jwt_identity()
    user_id = identity.get("user_id")
    email = identity.get("email")
    new_password = request_dynamic(request.is_json)('new_password')
    new_hash_code = get_hash_code(new_password)
    if user_id:
        # logged in user changing their password
        old_password = request_dynamic(request.is_json)('old_password')
        old_hash_code = select_hash_code(conn_info, user_id)
        if verify_hash_code(old_password, old_hash_code):
            rows_affected = update_hash_code(conn_info, new_hash_code, user_id=user_id)
            if rows_affected == 1:
                return jsonify(message="Password changed successfully.")
            else:
                return jsonify(message="That user does not exist or is not the requester."), 404
        else:
            return jsonify(message="Incorrect old password."), 400
    elif email:
        # user changing their password and clicked the reset link
        rows_affected = update_hash_code(conn_info, new_hash_code, email=email)
        if rows_affected == 1:
            return jsonify(message="Password changed successfully.")
        else:
            return jsonify(message="That user does not exist or is not the requester."), 404
    else:
        return jsonify(message="Unauthorized request to change password."), 401
