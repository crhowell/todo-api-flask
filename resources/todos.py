import datetime

from flask import jsonify, Blueprint, g

from flask_restful import (Resource, Api, reqparse,
                           inputs, fields, marshal, marshal_with)

from auth import auth
import models

todo_fields = {
    'name': fields.String,
    'description': fields.String,
    'created_at': fields.DateTime,
    'modified_on': fields.DateTime,
    'user': fields.String,
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'jsofn']
        )
        self.reqparse.add_argument(
            'description',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                 for todo in models.Todo.select()]
        return {'todos': todos}

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(
            created_at=datetime.datetime.now(),
            modified_on=datetime.datetime.now(),
            user=g.user,
            **args
        )
        return todo


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(TodoList, '/todos', endpoint='todos')
