from flask import g, make_response, jsonify

from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

import models

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Token')
auth = MultiAuth(token_auth, basic_auth)


@basic_auth.get_password
def get_password(username):
    user = models.User.get(username=username)
    if user is not None:
        return user.password
    return None


@basic_auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = models.User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = models.User.get(username=username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@token_auth.verify_token
def verify_token(token):
    if not token and g.user.is_authenticated:
        token = g.user.generate_auth_token()

    user = models.User.verify_auth_token(token)
    if user is not None:
        g.user = user
        return True
    return False


@basic_auth.error_handler
def unauthorized():
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)


@token_auth.error_handler
def auth_error():
    return make_response(jsonify({'message': 'Unauthorized access'}), 401)
