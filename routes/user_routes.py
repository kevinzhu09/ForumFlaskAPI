from routes.SQL_functions.users_table_SQL import *
from routes.routes_config import *

from constants import TIME_TO_EXPIRE, DESIRED_FIELDS
from hash_code_functions import *
from flask import jsonify, send_from_directory, request, Blueprint
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

basedir = path.abspath(path.dirname(__file__))
user_routes = Blueprint('user_routes', __name__, template_folder=path.join(basedir, '../templates'))


# Helper function that allows the API to accept a variable number of arguments.
def get_fields_from_request():
    return [request_dynamic(request.is_json, allow_null=True)(attribute) for attribute in DESIRED_FIELDS]


@user_routes.route('/api/verify', methods=['PUT'])
@jwt_required
def verify_account():
    identity = get_jwt_identity()
    email = identity.get("email")
    username = identity.get("username")
    if email_exists(conn_info, email):
        if username_exists(conn_info, username):
            return jsonify(message='That email is taken. That username is also taken.', code=3), 409
        else:
            return jsonify(message='That email is taken.', code=1), 409
    elif username_exists(conn_info, username):
        return jsonify(message='That username is taken.', code=2), 409
    unverified_user_id = identity.get("unverified_user_id")
    if email and unverified_user_id:
        password = request_dynamic(request.is_json)('password')
        print(password)
        if verify_hash_code(password, select_hash_code_from_unverified(conn_info, email, unverified_user_id)):

            rows_affected = verify_user(conn_info, email, unverified_user_id)
            if rows_affected == 1:
                access_token = create_access_token(identity={"user_id": unverified_user_id}, expires_delta=TIME_TO_EXPIRE)
                return jsonify(message="User verified successfully. Access token returned.", access_token=access_token, code=0)
            else:
                return jsonify(
                    message="That user is verified, does not exist or is not the requester, or some other issue.",
                    code=1), 404
        else:
            return jsonify(message="Unauthorized request to verify account. The password is wrong.", code=2), 401
    else:
        return jsonify(message="Unauthorized request to verify account.", code=4), 401


@user_routes.route('/api/login', methods=['POST'])
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
            return jsonify(message="Login succeeded! Access token returned.", access_token=access_token, code=0)
    return jsonify(message="Invalid email or password.", code=1), 401


@user_routes.route('/api/users', methods=['PUT'])
@jwt_required
def modify_user():
    user_id = get_jwt_identity().get("user_id")
    values_list = get_fields_from_request()
    rows_affected = update_user(*values_list, conn=conn_info, user_id=user_id)
    if rows_affected == 1:
        return jsonify(message="You updated a user.")
    else:
        return jsonify(message="That user does not exist."), 404


@user_routes.route('/api/users', methods=['DELETE'])
@jwt_required
def remove_user():
    user_id = get_jwt_identity().get("user_id")
    password = request_dynamic(request.is_json)('password')
    hash_code = select_hash_code(conn_info, user_id)
    verify = verify_hash_code(password, hash_code)
    if verify:
        rows_affected = delete_user(conn_info, user_id)
        if rows_affected == 1:
            return jsonify(message="You deleted a user.", code=0)
    else:
        return jsonify(message="Incorrect password.", code=1), 401


@user_routes.route('/api/users/<int:user_id>', methods=["GET"])
@jwt_required
def user_details_by_id(user_id: int):
    user = select_one_user(conn_info, 'user_id', user_id)
    if user:
        return jsonify(user)
    else:
        return jsonify(message="That user does not exist."), 404


@user_routes.route('/api/users', methods=["GET"])
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


@user_routes.route('/api/password/reset/confirm/', methods=['GET'])
def password_reset_confirm():
    return send_from_directory(directory='static', filename='password_reset_confirm.html')


@user_routes.route('/api/password', methods=['PUT'])
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
                return jsonify(message="Password changed successfully.", code=0)
            else:
                return jsonify(message="That user does not exist or is not the requester.", code=1), 404
        else:
            return jsonify(message="Incorrect old password.", code=2), 400
    elif email:
        # user changing their password and clicked the reset link
        rows_affected = update_hash_code(conn_info, new_hash_code, email=email)
        if rows_affected == 1:
            return jsonify(message="Password changed successfully.")
        else:
            return jsonify(message="That user does not exist or is not the requester.", code=3), 404
    else:
        return jsonify(message="Unauthorized request to change password.", code=4), 401


@user_routes.route('/api/authors/likes', methods=["GET"])
@jwt_required
def liked_authors():
    user_id = get_jwt_identity().get("user_id")
    if check_verified(conn_info, user_id):
        authors_list = select_liked_authors(conn_info, user_id)
        if authors_list:
            return jsonify(authors=authors_list, code=0)
        else:
            return jsonify(message="Authors do not exist.", code=1), 404
    else:
        return jsonify(message="Unauthorized request to view authors.", code=2), 401


@user_routes.route('/api/authors/likes/<int:author_id>', methods=["POST"])
@jwt_required
def like_authors(author_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_author(conn_info, author_id, user_id):
        return jsonify(message="Author is already liked.", code=0)
    else:
        insert_liked_author(conn_info, author_id, user_id)
        return jsonify(message="Author has been liked.", code=0)


@user_routes.route('/api/authors/likes/<int:author_id>', methods=["DELETE"])
@jwt_required
def unlike_authors(author_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_author(conn_info, author_id, user_id):
        delete_liked_author(conn_info, author_id, user_id)
        return jsonify(message="Author has been unliked.", code=0)
    else:
        return jsonify(message="Author is already unliked.", code=0)
