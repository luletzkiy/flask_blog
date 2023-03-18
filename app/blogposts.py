from flask import Blueprint, request, jsonify
from app.database import Blogpost, User, db
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.constants.http_status_codes import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_404_NOT_FOUND,HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

blogposts = Blueprint("blogposts",__name__,url_prefix="/api/v1/blogposts")

@blogposts.route('/', methods=['GET'])
def get_blogposts():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    blogposts = Blogpost.query.paginate(page=page, per_page=per_page)

    data = []

    for blogpost in blogposts.items:
        data.append({
        'id': blogpost.id,
        'name': blogpost.name,
        'content': blogpost.content,
        'visits': blogpost.visits,
        'author': User.query.filter_by(id=blogpost.user_id).first().username,
        'created_at': blogpost.created_at,
        'updated_at': blogpost.updated_at})

    meta={
        'page': blogposts.page,
        'pages': blogposts.pages,
        'total_count': blogposts.total,
        'prev_page': blogposts.prev_num,
        'next_page': blogposts.next_num,
        'has_next': blogposts.has_next,
        'has_prev': blogposts.has_prev 
        }
        
    return jsonify({'data': data, 'meta': meta}), HTTP_200_OK

@blogposts.post('/create')
@jwt_required()
def create_blogpost():
    current_user = get_jwt_identity()

    if request.method == 'POST':
        name = request.get_json().get('name', '')
        content = request.get_json().get('content', '')
        
        if Blogpost.query.filter_by(name=name).first():
            return jsonify({
                'error': "Blogpost with such name already exists"
            }), HTTP_409_CONFLICT
        
        blogpost = Blogpost(name=name, content=content, user_id=current_user)
        db.session.add(blogpost)
        db.session.commit()

        return jsonify({
        'id': blogpost.id,
        'name': blogpost.name,
        'content': blogpost.content,
        'visits': blogpost.visits,
        'author': User.query.filter_by(id=blogpost.user_id).first().username,
        'created_at': blogpost.created_at,
        'updated_at': blogpost.updated_at}), HTTP_201_CREATED
    
@blogposts.put('/edit/<int:id>')
@blogposts.patch('/edit/<int:id>')
@jwt_required()
def edit_blogpost(id):
    current_user = get_jwt_identity()

    blogpost = Blogpost.query.filter_by(id=id).first()

    if not blogpost:
        return jsonify({
            'message': "Item not found"
        }), HTTP_404_NOT_FOUND
    
    if not blogpost.user_id==current_user:
        return jsonify({
            'message': "You can't edit this post"
        }), HTTP_403_FORBIDDEN

    name = request.get_json().get('name', '')
    content = request.get_json().get('content', '')
    
    blogpost.name=name
    blogpost.content=content

    db.session.commit()

    return jsonify({
        'id': blogpost.id,
        'name': blogpost.name,
        'content': blogpost.content,
        'visits': blogpost.visits,
        'author': User.query.filter_by(id=blogpost.user_id).first().username,
        'created_at': blogpost.created_at,
        'updated_at': blogpost.updated_at}), HTTP_200_OK


@blogposts.delete("/delete/<int:id>")
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()

    blogpost = Blogpost.query.filter_by(id=id).first()

    if not blogpost:
        return jsonify({
            'message': "Item not found"
        }), HTTP_404_NOT_FOUND
    
    if not blogpost.user_id==current_user:
        return jsonify({
            'message': "You can't delete this post"
        }), HTTP_403_FORBIDDEN

    db.session.delete(blogpost)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT

@blogposts.get('/get/<int:id>')
def get_blogpost(id):
    blogpost = Blogpost.query.filter_by(id=id).first()

    if not blogpost:
        return jsonify({
            'message': "Item not found"
        }), HTTP_404_NOT_FOUND
    
    return jsonify({
        'id': blogpost.id,
        'name': blogpost.name,
        'content': blogpost.content,
        'visits': blogpost.visits,
        'author': User.query.filter_by(id=blogpost.user_id).first().username,
        'created_at': blogpost.created_at,
        'updated_at': blogpost.updated_at}), HTTP_200_OK