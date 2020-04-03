from routes.SQL_functions.posts_table_SQL import *
from routes.SQL_functions.users_table_SQL import select_liked_author
from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from routes.routes_config import *

basedir = path.abspath(path.dirname(__file__))
post_routes = Blueprint('post_routes', __name__, template_folder=path.join(basedir, '../templates'))


@post_routes.route('/posts', methods=['POST'])
@jwt_required
def create_post():
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        title = request_dynamic(request.is_json)('title')
        content = request_dynamic(request.is_json)('content')
        post_id = insert_post(conn=conn_info, author_id=author_id, title=title, content=content)
        return jsonify(message="Post created successfully.", post_id=post_id, code=0), 201
    else:
        return jsonify(message="Unauthorized request to create post.", code=1), 401


@post_routes.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required
def remove_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        rows_affected = delete_post(conn_info, post_id, author_id)
        if rows_affected == 1:
            return jsonify(message="You deleted a post.", code=0)
        else:
            return jsonify(message="That post does not both exist and belong to the requester.", code=1), 404
    else:
        return jsonify(message="Unauthorized request to delete post.", code=2), 401


@post_routes.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required
def modify_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        content = request_dynamic(request.is_json)('content')
        rows_affected = update_post(conn_info, post_id, author_id, content)
        if rows_affected == 1:
            return jsonify(message="You updated a post.", code=0)
        else:
            return jsonify(message="That post does not both exist and belong to the requester."), 404
    else:
        return jsonify(message="Unauthorized request to modify post."), 401


@post_routes.route('/posts/<int:post_id>', methods=["GET"])
@jwt_required
def post_details(post_id: int):
    post = select_post_including_content(conn_info, post_id)
    if post:
        author_id = post['author_id']
        user_id = get_jwt_identity().get("user_id")
        own_post = author_id == user_id
        return jsonify(post_details=post, own_post=own_post, liked_status=select_liked_post(conn_info, post_id, user_id),
                       code=0)
    else:
        return jsonify(message="That post does not exist.", code=1), 404


@post_routes.route('/posts', methods=["GET"])
@jwt_required
def posts():
    user_id = get_jwt_identity().get("user_id")
    verified_username = check_verified(conn_info, user_id)
    if verified_username:
        posts_list = select_recent_posts(conn_info)
        if posts_list:
            return jsonify(posts=posts_list, userUsername=verified_username, code=0)
        else:
            return jsonify(message="Posts do not exist.", userUsername=verified_username, code=1), 404
    else:
        return jsonify(message="Unauthorized request to view posts.", code=2), 401


@post_routes.route('/authors/<int:author_id>', methods=["GET"])
@jwt_required
def author_posts(author_id: int):
    user_id = get_jwt_identity().get("user_id")
    if check_verified(conn_info, user_id):
        if user_id == author_id:
            return jsonify(code=0, ownPage=True)
        if author_id == 0:
            posts_list_and_username = select_recent_posts_from_author(conn_info, user_id)
        else:
            posts_list_and_username = select_recent_posts_from_author(conn_info, author_id)
        posts_list = posts_list_and_username[0]
        author_username = posts_list_and_username[1]
        if posts_list:
            return jsonify(posts=posts_list, authorUsername=author_username, code=0, ownPage=False, id=user_id, liked_status=select_liked_author(conn_info, author_id, user_id),)
        elif author_username:
            return jsonify(message="That author's posts do not exist.", authorUsername=author_username, code=1), 404
        else:
            return jsonify(message="That author does not exist.", code=2), 404
    else:
        return jsonify(message="Unauthorized request to view posts.", code=3), 401


@post_routes.route('/posts/likes', methods=["GET"])
@jwt_required
def liked_posts():
    user_id = get_jwt_identity().get("user_id")
    verified_username = check_verified(conn_info, user_id)
    if verified_username:
        posts_list = select_liked_posts(conn_info, user_id)
        if posts_list:
            return jsonify(posts=posts_list, userUsername=verified_username, code=0)
        else:
            return jsonify(message="Posts do not exist.", userUsername=verified_username, code=1), 404
    else:
        return jsonify(message="Unauthorized request to view posts.", code=2), 401


@post_routes.route('/posts/likes/<int:post_id>', methods=["POST"])
@jwt_required
def like_posts(post_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_post(conn_info, post_id, user_id):
        return jsonify(message="Post is already liked.", code=0)
    else:
        insert_liked_post(conn_info, post_id, user_id)
        return jsonify(message="Post has been liked.", code=0)


@post_routes.route('/posts/likes/<int:post_id>', methods=["DELETE"])
@jwt_required
def unlike_posts(post_id: int):
    user_id = get_jwt_identity().get("user_id")
    if select_liked_post(conn_info, post_id, user_id):
        delete_liked_post(conn_info, post_id, user_id)
        return jsonify(message="Post has been unliked.", code=0)
    else:
        return jsonify(message="Post is already unliked.", code=0)

# @post_routes.route('/posts/likes/<int:post_id>', methods=["GET"])
# @jwt_required
# def post_liked_status(post_id: int):
#     user_id = get_jwt_identity().get("user_id")
#     return jsonify(liked_status=select_liked_post(conn_info, post_id, user_id), code=0)
