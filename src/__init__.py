from flask import Flask, redirect
import os 
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__,
                instance_relative_config=True)
    
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DATABASE_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'), 
        )
    else:
        app.config.from_mapping(test_config)
    
    db.app = app
    db.init_app(app)
    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    @app.get('/<short_url>')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits += 1
            db.session.commit()
            return redirect(bookmark.url)


    @app.errorhandler(404)
    def handle_404(e):
        return {'error': 'Not Found'}, 404
    @app.errorhandler(500)
    def handle_500(e):
        return {'error': 'Something went wrong'}, 500

    return app