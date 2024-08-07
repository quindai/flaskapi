from enum import unique
from flask_sqlalchemy import SQLAlchemy
import string, random
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks=db.relationship('Bookmark',backref='user',lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_characters(self):
        picked_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=3))
        link = self.query.filter_by(short_url=picked_char).first()
        if link:
            self.generate_short_characters()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_characters()
    
    def __repr__(self):
        return f'<Bookmark {self.title}>'