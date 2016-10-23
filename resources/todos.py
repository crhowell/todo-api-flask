import datetime
import json

from flask import Blueprint, g, abort, make_response

from flask_restful import (Resource, Api, reqparse, url_for,
                           inputs, fields, marshal)

from auth import auth
import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'completed': fields.Boolean,
    'created_at': fields.DateTime,
    'modified_on': fields.DateTime
}


def todo_or_404(todo_id):
    try:
        todo = models.Todo.get(id=todo_id)
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
        self.reqparse.add_argument(
            'completed',
            required=False,
            default=False,
            type=inputs.boolean,
            location=['form', 'json']
        )
        super().__init__()

    def get(self):
        todos = models.Todo.select().order_by(
            models.Todo.created_at.desc(), models.Todo.completed)
        return [marshal(todo, todo_fields) for todo in todos]

    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(
            created_at=datetime.datetime.now(),
            modified_on=datetime.datetime.now(),
            user=g.user.id,
            **args
        )
        return (marshal(todo, todo_fields), 201, {
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
        self.reqparse.add_argument(
            'completed',
            required=False,
            default=False,
            type=inputs.boolean,
            location=['form', 'json']
        )
        super().__init__()

    def get(self, id):
        return (marshal(todo_or_404(id), todo_fields), 200, {
            'Location': url_for('resources.todos.todo', id=id)
        })

    @auth.login_required
    def put(self, id):
        args = self.reqparse.parse_args()
        try:
            todo = todo_or_404(id)
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That review does not exist or is not editable'}
            ), 403)

        # Make sure current user owns task.
        if todo.user.id != g.user.id:
            return make_response(json.dumps(
                {'error': 'You cannot update this task because you are not the owner.'}
            ), 401)

        query = todo.update(
            modified_on=datetime.datetime.now(),
            **args
        ).where(models.Todo.id == id)

        query.execute()
        return (marshal(todo_or_404(id), todo_fields), 200, {
            'Location': url_for('resources.todos.todo', id=id)
        })

    @auth.login_required
    def delete(self, id):
        try:
            todo = todo_or_404(id)
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'That TODO  does not exist or is not editable'}
            ), 403)
        # Make sure current user owns task.
        if todo.user.id != g.user.id:
            return make_response(json.dumps(
                {'error': 'You cannot delete this task because you are not the owner.'}
            ), 401)

        todo.delete_instance()
        return '', 204, {'Location': url_for('resources.todos.todos')}


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(TodoList, '/todos', endpoint='todos')
api.add_resource(Todo, '/todos/<int:id>', endpoint='todo')
