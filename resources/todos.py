from flask import jsonify, Blueprint

from flask_restful import (Resource, Api, reqparse,
                           inputs, fields, marshal, marshal_with)

import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'created_at': fields.DateTime,
    'modified_on': fields.DateTime,
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields)
                 for todo in models.Todo.select()]
        return {'todos': todos}

    def post(self):
        args = self.reqparse.parse_args()
        models.Course.create(**args)
        return jsonify({'todos': [{'name': 'Our First Task TODO'}]})


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(TodoList, '/todos', endpoint='todos')
#api.add_resource()

