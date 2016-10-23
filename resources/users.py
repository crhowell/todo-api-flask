import json
from flask import jsonify, Blueprint, make_response, abort, g

from flask_restful import (Resource, Api, reqparse,
                           inputs, fields, marshal, marshal_with)
from auth import auth
import models

user_fields = {
    'username': fields.String
}


def user_or_404(username, password):
    try:
        user = models.User.get(username==username)
    except models.User.DoesNotExist:
        abort(404)
    else:
        if user and user.verify_password(password):
            return user
    return None


class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'verify_password',
            required=True,
            help='No password verification provided',
            location=['form', 'json']
        )
        super().__init__()

    def post(self):
        args = self.reqparse.parse_args()
        if args.get('password') == args.get('verify_password'):
            user = models.User.create_user(**args)
            return marshal(user, user_fields), 201
        return make_response(
            json.dumps(
                {'error': 'Password and password verification do not match.'}), 400
        )


class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()

    @auth.login_required
    def get(self):
        token = g.user.generate_auth_token()
        return jsonify({'token': token.decode('ascii')})


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(UserList, '/users', endpoint='users')
api.add_resource(User, '/users/token', endpoint='token')
