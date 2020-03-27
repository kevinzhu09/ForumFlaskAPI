from config.app_config import *
from SQL_functions.posts_table_SQL import *
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity


@app.route('/posts', methods=['POST'])
@jwt_required
def create_post():
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        title = request_dynamic(request.is_json)('title')
        content = request_dynamic(request.is_json)('content')
        insert_post(conn_info=conn_info, author_id=author_id, title=title, content=content)
        return jsonify(message="Post created successfully."), 201
    else:
        return jsonify(message="Unauthorized request to create post."), 401


@app.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required
def remove_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        rows_affected = delete_post(conn_info, post_id, author_id)
        if rows_affected == 1:
            return jsonify(message="You deleted a post.")
        else:
            return jsonify(message="That post does not both exist and belong to the requester."), 404
    else:
        return jsonify(message="Unauthorized request to delete post."), 401


@app.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required
def modify_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        content = request_dynamic(request.is_json)('content')
        rows_affected = update_post(conn_info, post_id, author_id, content)
        if rows_affected == 1:
            return jsonify(message="You updated a post.")
        else:
            return jsonify(message="That post does not both exist and belong to the requester."), 404
    else:
        return jsonify(message="Unauthorized request to modify post."), 401


@app.route('/posts/<int:post_id>', methods=["GET"])
@jwt_required
def post_details(post_id: int):
    content_and_author_id = select_post_content_and_author_id(conn_info, post_id)
    if content_and_author_id:
        content = content_and_author_id[0]
        author_id = content_and_author_id[1]
        own_post = author_id == get_jwt_identity().get("user_id")
        return jsonify(content=content, ownPost=own_post)
    else:
        return jsonify(message="That user does not exist."), 404


@app.route('/posts', methods=["GET"])
@jwt_required
def posts():
    posts_list = select_recent_posts(conn_info)
    if posts_list:
        return jsonify(posts_list)
    else:
        return jsonify(message="Posts do not exist."), 404


@app.route('/authors/<int:author_id>', methods=["GET"])
@jwt_required
def author_posts(author_id: int):
    posts_list = select_recent_posts_from_author(conn_info, author_id)
    if posts_list:
        return jsonify(posts_list)
    else:
        return jsonify(message="That author does not exist."), 404
