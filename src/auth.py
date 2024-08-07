from flask import Blueprint, request, jsonify
from src.constants.http_status_codes import (
    HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_200_OK)
from werkzeug.security import (
    generate_password_hash, check_password_hash
)
from src.database import User, db
#import validators
from flask_jwt_extended import (
    jwt_required, create_access_token, create_refresh_token, get_jwt_identity
)
auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.post('/login')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    print("Entrou")
    if user is None or not check_password_hash(user.password, password):
        return jsonify({
            'error': 'Credenciais Inválidas'}
            ), HTTP_400_BAD_REQUEST

    refresh = create_refresh_token(identity=user.id)
    access = create_access_token(identity=user.id)
    return jsonify({
        'message': 'Login successful',
        'user': {
            'refresh_token': refresh,
            'access_token': access,
            'username': user.username, 
            'email': user.email}
        }), HTTP_200_OK

@auth.post('/register')
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    if len(password) < 6:
        return jsonify({
            'error': 'Password must be at least 6 characters long'}
            ), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({
            'error': 'Username must be at least 3 characters long'}
            ), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({
            'error': 'Username must be alphanumeric and without spaces'}
            ), HTTP_400_BAD_REQUEST

    # if not validators.email(email):
    #     return jsonify({
    #         'error': 'Invalid email'}
    #         ), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({
            'error': 'Email already exists'}
            ), HTTP_409_CONFLICT 
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'error': 'Username is taken'}
            ), HTTP_409_CONFLICT 

    pwd_hash=generate_password_hash(password)
    user = User(username=username, email=email, password=pwd_hash)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'user': {'username': user.username, 'email': user.email }
        }), HTTP_201_CREATED

@auth.get('/me')
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email': user.email
    }), HTTP_200_OK


@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_user_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({
        'access_token': access_token
    }), HTTP_200_OK