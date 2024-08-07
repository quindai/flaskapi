import validators
import src.constants.http_status_codes as code
from src.database import db, Bookmark
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks')

# @bookmarks.get('/')
# def index():
#     return []

@bookmarks.route('/', methods=['GET','POST'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'GET':
        bookmarks = Bookmark.query.filter_by(user_id=current_user).all()
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

        return jsonify({'data': data}), code.HTTP_200_OK
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
      