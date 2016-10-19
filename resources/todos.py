import datetime
import json

from flask import jsonify, Blueprint, g, abort, make_response

from flask_restful import (Resource, Api, reqparse, url_for,
                           inputs, fields, marshal, marshal_with)

from auth import auth
import models

todo_fields = {
    'name': fields.String,
    'created_at': fields.DateTime,
    'modified_on': fields.DateTime,
    'user': fields.String,
}


def todo_or_404(todo_id):
    try:
        todo = models.Todo.get(models.Todo.id==todo_id)
    except models.Todo.DoesNotExist:
        abort(404)
    else:
        return todo


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
        return todos

    @marshal_with(todo_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(
            created_at=datetime.datetime.now(),
            modified_on=datetime.datetime.now(),
            user=g.user,
            **args
        )
        return (todo, 201, {
            'Location': url_for('resources.todos.todo', id=todo.id)
        })


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No todo name provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

    @marshal_with(todo_fields)
    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            todo = models.Todo.select().where(
                models.Todo.user==g.user,
                models.Todo.id==id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)
        query = todo.update(**args)
        query.execute()
        todo = todo_or_404(id)
        return (todo, 200, {
            'Location': url_for('resources.todos.todo', id=id)
        })

    @auth.login_required
    def delete(self, id):
        try:
            todo = models.Todo.select().where(
                models.Todo.user==g.user,
                models.Todo.id==id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That TODO  does not exist or is not editable'}
            ), 403)
        query = todo.delete()
        query.execute()
        return '', 204, {'Location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(TodoList, '/todos', endpoint='todos')
api.add_resource(Todo, '/todos/<int:id>', endpoint='todo')
