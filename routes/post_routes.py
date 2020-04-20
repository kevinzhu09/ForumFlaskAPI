from routes.data_access.posts_data_access import insert_post, delete_post, select_post_including_content, \
    liked_post_exists, select_recent_posts, insert_liked_post, insert_image, select_image, delete_liked_post, \
    select_recent_posts_from_author, select_liked_posts, update_post
from routes.data_access.users_data_access import select_liked_author
from flask import jsonify, Blueprint, send_file, request
from flask_jwt_extended import jwt_required, get_jwt_identity, jwt_optional
from routes.routes_config import request_dynamic, check_regular_user_verified_username
from io import BytesIO
from os import path

basedir = path.abspath(path.dirname(__file__))
post_routes = Blueprint('post_routes', __name__, template_folder=path.join(basedir, '../templates'))


@post_routes.route('/api/posts', methods=['POST'])
@jwt_required
def create_post():
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        title = request_dynamic(request.is_json)('title')
        content = request_dynamic(request.is_json)('content')
        post_id = insert_post(author_id=author_id, title=title, content=content)
        return jsonify(message="Post created successfully.", post_id=post_id, code=0), 201
    else:
        return jsonify(message="Unauthorized request to create post.", code=1), 401


@post_routes.route('/api/posts/<int:post_id>', methods=['DELETE'])
@jwt_required
def remove_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        delete_post(post_id, author_id)
        return jsonify(message="You deleted a post.", code=0)
    else:
        return jsonify(message="Unauthorized request to delete post.", code=2), 401


@post_routes.route('/api/posts/<int:post_id>', methods=['PUT'])
@jwt_required
def modify_post(post_id: int):
    author_id = get_jwt_identity().get("user_id")
    if author_id:
        content = request_dynamic(request.is_json)('content')
        update_post(content, post_id, author_id)
        return jsonify(message="You updated a post.", code=0)
    else:
        return jsonify(message="Unauthorized request to modify post."), 401


@post_routes.route('/api/posts/<int:post_id>', methods=["GET"])
@jwt_optional
def post_details(post_id: int):
    post = select_post_including_content(post_id)
    if post:
        author_id = post['author_id']
        current_user = get_jwt_identity()
        if current_user:
            user_id = current_user.get("user_id")
            verified_username = check_regular_user_verified_username(user_id)
            if verified_username:
                own_post = author_id == user_id
                return jsonify(post_details=post, own_post=own_post,
                               liked_status=liked_post_exists(post_id, user_id),
                               userUsername=verified_username,
                               code=0), 200
            else:
                return jsonify(message="Unauthorized request to view posts.", code=2), 401
        else:
            return jsonify(post_details=post, logged_in_as='guest', code=0), 200
    else:
        return jsonify(message="That post does not exist.", code=1), 404


@post_routes.route('/api/posts', methods=["GET"])
@jwt_optional
def posts():
    current_user = get_jwt_identity()
    posts_list = select_recent_posts()
    if current_user:
        user_id = current_user.get("user_id")
        verified_username = check_regular_user_verified_username(user_id)
        if verified_username:
            if posts_list:
                return jsonify(posts=posts_list, userUsername=verified_username, code=0)
            else:
                return jsonify(message="There are no posts.", userUsername=verified_username, code=1)
        else:
            return jsonify(message="Unauthorized request to view posts.", code=2), 401
    else:
        if posts_list:
            return jsonify(posts=posts_list, logged_in_as='guest', code=0), 200
        else:
            return jsonify(message="There are no posts.", logged_in_as='guest', code=1)


@post_routes.route('/api/authors/<int:author_id>', methods=["GET"])
@jwt_optional
def author_posts(author_id: int):
    current_user = get_jwt_identity()
    if current_user:
        user_id = current_user.get("user_id")
        verified_username = check_regular_user_verified_username(user_id)
        if verified_username:
            if user_id == author_id:
                return jsonify(code=0, ownPage=True)
            if author_id == 0:
                posts_list_and_username = select_recent_posts_from_author(user_id)
            else:
                posts_list_and_username = select_recent_posts_from_author(author_id)
            posts_list = posts_list_and_username[0]
            author_username = posts_list_and_username[1]
            if posts_list:
                return jsonify(posts=posts_list, authorUsername=author_username, code=0, ownPage=False, id=user_id,
                               liked_status=select_liked_author(author_id, user_id), userUsername=verified_username)
            elif author_username:
                return jsonify(message="That author has no posts.", authorUsername=author_username, code=1, userUsername=verified_username)
            else:
                return jsonify(message="That author does not exist.", code=2, userUsername=verified_username), 404
        else:
            return jsonify(message="Unauthorized request to view posts.", code=3), 401
    else:
        posts_list_and_username = select_recent_posts_from_author(author_id)
        posts_list = posts_list_and_username[0]
        author_username = posts_list_and_username[1]
        if posts_list:
            return jsonify(posts=posts_list, authorUsername=author_username, logged_in_as='guest', code=0), 200
        elif author_username:
            return jsonify(message="That author has no posts.", authorUsername=author_username, logged_in_as='guest', code=1)
        else:
            return jsonify(message="That author does not exist.", logged_in_as='guest', code=2), 404


@post_routes.route('/api/posts/likes', methods=["GET"])
@jwt_required
def liked_posts():
    user_id = get_jwt_identity().get("user_id")
    verified_username = check_regular_user_verified_username(user_id)
    if verified_username:
        posts_list = select_liked_posts(user_id)
        if posts_list:
            return jsonify(posts=posts_list, userUsername=verified_username, code=0)
        else:
            return jsonify(message="The user has not liked any posts.", userUsername=verified_username, code=1)
    else:
        return jsonify(message="Unauthorized request to view posts.", code=2), 401


@post_routes.route('/api/posts/likes/<int:post_id>', methods=["POST"])
@jwt_required
def like_posts(post_id: int):
    user_id = get_jwt_identity().get("user_id")
    if liked_post_exists(post_id, user_id):
        return jsonify(message="Post is already liked.", code=0)
    else:
        insert_liked_post(post_id, user_id)
        return jsonify(message="Post has been liked.", code=0)


@post_routes.route('/api/posts/likes/<int:post_id>', methods=["DELETE"])
@jwt_required
def unlike_posts(post_id: int):
    user_id = get_jwt_identity().get("user_id")
    if liked_post_exists(post_id, user_id):
        delete_liked_post(post_id, user_id)
        return jsonify(message="Post has been unliked.", code=0)
    else:
        return jsonify(message="Post is already unliked.", code=0)


@post_routes.route('/api/images', methods=["POST"])
@jwt_required
def images_post():
    user_id = get_jwt_identity().get("user_id")
    if check_regular_user_verified_username(user_id):
        file = request.files.get('file', None)
        if file:
            image_data = file.read()
            mimetype = file.mimetype
            if mimetype.startswith('image/', 0, 6):
                mimetype_ext = mimetype[6:10]

                image_id = insert_image(image_data, user_id, mimetype_ext)
                return jsonify(code=0, url=request.base_url + "/" + str(image_id))
            else:
                return jsonify(code=3, message="The uploaded file did not begin with image/.")
        else:
            return jsonify(code=2, message="Uploaded file was not found.")
    else:
        return jsonify(code=1, message="Unauthorized request to upload image"), 401


@post_routes.route('/api/images/<int:image_id>', methods=["GET"])
def images_get(image_id: int):
    image = select_image(image_id)
    return send_file(BytesIO(image["image_data"]), "image/" + image['mime_type'])
