from routes.data_access.users_data_access import email_exists, username_exists, \
    select_unverified_regular_user_hash_code, verify_regular_user, select_regular_user_hash_code, \
    select_regular_user_hash_code_and_id, update_regular_user_hash_code, select_liked_author, select_liked_authors, \
    insert_liked_author, delete_user, delete_liked_author, check_social_login
from routes.routes_config import request_dynamic, check_regular_user_verified_username
from os import path

from hash_code_functions import verify_hash_code, get_hash_code
from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from config.APIConfig import TOKEN_TTL_TIMEDELTA

basedir = path.abspath(path.dirname(__file__))
user_routes = Blueprint('user_routes', __name__, template_folder=path.join(basedir, '../templates'))


@user_routes.route('/api/verify', methods=['PUT'])
@jwt_required
def verify_account():
    identity = get_jwt_identity()
    email = identity.get("email")
    username = identity.get("username")
    if email_exists(email, False):
        if username_exists(username, False):
            return jsonify(message='That email is taken. That username is also taken.', code=3), 409
        else:
            return jsonify(message='That email is taken.', code=4), 409
    elif username_exists(username, False):
        return jsonify(message='That username is taken.', code=5), 409
    unverified_user_id = identity.get("unverified_user_id")
    if email and unverified_user_id:
        password = request_dynamic(request.is_json)('password')
        if verify_hash_code(password, select_unverified_regular_user_hash_code(email, unverified_user_id)):
            verify_regular_user(email, unverified_user_id)
            access_token = create_access_token(identity={"user_id": unverified_user_id},
                                               expires_delta=TOKEN_TTL_TIMEDELTA)
            return jsonify(message="User verified successfully. Access token returned.", access_token=access_token,
                           code=0)
        else:
            return jsonify(message="Unauthorized request to verify account. The password is wrong.", code=1), 401
    else:
        return jsonify(message="Unauthorized request to verify account.", code=2), 401


@user_routes.route('/api/login', methods=['POST'])
def regular_login():
    email = request_dynamic(request.is_json)('email')
    password = request_dynamic(request.is_json)('password')

    hash_code_and_id = select_regular_user_hash_code_and_id(email)
    if hash_code_and_id:
        hash_code = hash_code_and_id[0]
        verify = verify_hash_code(password, hash_code)
        if verify:
            user_id = hash_code_and_id[1]
            access_token = create_access_token(identity={"user_id": user_id}, expires_delta=TOKEN_TTL_TIMEDELTA)
            return jsonify(message="Login succeeded! Access token returned.", access_token=access_token, code=0)
    return jsonify(message="Invalid email or password.", code=1), 401


@user_routes.route('/api/refresh', methods=['POST'])
@jwt_required
def refresh_login():
    current_user = get_jwt_identity()
    if current_user:
        user_id = current_user.get("user_id")
        if user_id:
            verified_username = check_regular_user_verified_username(user_id)
            if verified_username:
                access_token = create_access_token(identity={"user_id": user_id}, expires_delta=TOKEN_TTL_TIMEDELTA)
                return jsonify(message="Refresh succeeded. Access token returned.", access_token=access_token, userUsername=verified_username, code=0), 200

    return jsonify(message="Unauthorized request to refresh token.", code=1), 401


@user_routes.route('/api/users', methods=['DELETE'])
@jwt_required
def remove_user():
    user_id = get_jwt_identity().get("user_id")
    if check_social_login(user_id):
        return jsonify(message="Cannot delete social login account.", code=2)
    else:
        password = request_dynamic(request.is_json)('password')
        hash_code = select_regular_user_hash_code(user_id)
        verify = verify_hash_code(password, hash_code)
        if verify:
            delete_user(user_id)
            return jsonify(message="You deleted a user.", code=0)
        else:
            return jsonify(message="Incorrect password.", code=1), 401


@user_routes.route('/api/password', methods=['PUT'])
@jwt_required
def change_password():
    identity = get_jwt_identity()
    user_id = identity.get("user_id")
    email = identity.get("email")
    new_password = request_dynamic(request.is_json)('new_password')
    new_hash_code = get_hash_code(new_password)
    if user_id:
        if check_social_login(user_id):
            return jsonify(message="Cannot change password of social login account.", code=3)
        else:
            old_password = request_dynamic(request.is_json)('old_password')
            old_hash_code = select_regular_user_hash_code(user_id)
            if verify_hash_code(old_password, old_hash_code):
                update_regular_user_hash_code(new_hash_code, user_id=user_id)
                return jsonify(message="Password changed successfully.", code=0)
            else:
                return jsonify(message="Incorrect old password.", code=2), 400
    elif email:
        user_id = update_regular_user_hash_code(new_hash_code, email=email)
        access_token = create_access_token(identity={"user_id": user_id}, expires_delta=TOKEN_TTL_TIMEDELTA)
        return jsonify(message="Password reset successfully. Access token returned.", access_token=access_token,
                       code=0)
    else:
        return jsonify(message="Unauthorized request to change password.", code=4), 401


@user_routes.route('/api/authors/likes', methods=["GET"])
@jwt_required
def liked_authors():
    user_id = get_jwt_identity().get("user_id")
    if check_regular_user_verified_username(user_id):
        authors_list = select_liked_authors(user_id)
        if authors_list:
            return jsonify(authors=authors_list, code=0)
        else:
            return jsonify(message="The user has not liked any authors.", code=1)
    else:
        return jsonify(message="Unauthorized request to view authors.", code=2), 401


@user_routes.route('/api/authors/likes/<int:author_id>', methods=["POST"])
@jwt_required
def like_authors(author_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_author(author_id, user_id):
        return jsonify(message="Author is already liked.", code=0)
    else:
        insert_liked_author(author_id, user_id)
        return jsonify(message="Author has been liked.", code=0)


@user_routes.route('/api/authors/likes/<int:author_id>', methods=["DELETE"])
@jwt_required
def unlike_authors(author_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_author(author_id, user_id):
        delete_liked_author(author_id, user_id)
        return jsonify(message="Author has been unliked.", code=0)
    else:
        return jsonify(message="Author is already unliked.", code=0)


@user_routes.route('/api/users/username', methods=["GET"])
@jwt_required
def get_username():
    user_id = get_jwt_identity().get("user_id")
    verified_username = check_regular_user_verified_username(user_id)
    if verified_username:
        return jsonify(userUsername=verified_username, socialLogin=check_social_login(user_id), code=0), 200
    else:
        return jsonify(message="Unauthorized request to get username.", code=1), 401
