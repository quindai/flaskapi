import validators
import src.constants.http_status_codes as code
from src.database import db, Bookmark
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')

# @bookmarks.get('/')
# def index():
#     return []

@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), code.HTTP_404_NOT_FOUND
    return jsonify({
        'id': bookmark.id,
        'body': bookmark.body,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visits': bookmark.visits,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), code.HTTP_200_OK

@bookmarks.route('/', methods=['GET','POST'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'GET':
        page=request.args.get('page',1,type=int)
        per_page=request.args.get('per_page',5,type=int)
        bookmarks = Bookmark.query.filter_by(
            user_id=current_user
            ).paginate(page=page,per_page=per_page)
        
        data = []

        for bookmark in bookmarks:
            data.append({
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at,
            })

        meta = {
            'page': bookmarks.page,
            'pages': bookmarks.pages,
            'per_page': bookmarks.per_page,
            'total': bookmarks.total,
            'prev': bookmarks.prev_num,
            'next': bookmarks.next_num,
            'has_next': bookmarks.has_next,
            'has_prev': bookmarks.has_prev,
        }

        return jsonify({'data': data, 'meta': meta}), code.HTTP_200_OK
    elif request.method == 'POST':
        body = request.json.get('body','')
        url = request.json.get('url','')

        if not validators.url(url):
            return jsonify({'error': 'Invalid URL'}), code.HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({'error': 'URL already in use'}), code.HTTP_409_CONFLICT
        
        bookmark = Bookmark(body=body, url=url, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()
        return jsonify({
            'message': 'Bookmark created',
            'bookmark': {
                'id': bookmark.id,
                'body': bookmark.body,
                'url': bookmark.url,
                'short_url': bookmark.short_url,
                'visits': bookmark.visits,
                'created_at': bookmark.created_at,
                'updated_at': bookmark.updated_at,
            }
        }), code.HTTP_201_CREATED
      
@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def update_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), code.HTTP_404_NOT_FOUND
    body = request.json.get('body', '')
    url = request.json.get('url', '')

    if not validators.url(url):
        return jsonify({'error': 'Invalid URL'}), code.HTTP_400_BAD_REQUEST
    
    if Bookmark.query.filter_by(url=url).first():
        return jsonify({'error': 'URL already in use'}), code.HTTP_409_CONFLICT
    
    bookmark.body = body
    bookmark.url = url
    db.session.commit()
    return jsonify({
        'message': 'Bookmark updated',
        'bookmark': {
            'id': bookmark.id,
            'body': bookmark.body,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
        }
    }), code.HTTP_200_OK

@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), code.HTTP_404_NOT_FOUND
    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({'message': 'Bookmark deleted'}), code.HTTP_204_NO_CONTENT

@bookmarks.get('/stats')
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    data = []
    items = Bookmark.query.filter_by(user_id=current_user).all()

    for item in items:
        new_link = {
            'id': item.id,
            'url': item.url,
            'short_url': item.short_url,
            'visits': item.visits,
        }
        data.append(new_link)
    return jsonify({'data':data}), code.HTTP_200_OK