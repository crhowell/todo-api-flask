import unittest
import json

from playhouse.test_utils import test_database
from peewee import *

from app import app
from models import User, Todo


USER_DATA = {
    'username': 'test_user_0',
    'email': 'test_0@example.com',
    'password': 'password'
}
TODO_LIST = ['Walk the dog', 'Take out the trash', 'Wash the dishes']


class TodoTestCase(unittest.TestCase):

    @staticmethod
    def create_test_todos(user=1):
        for todo in TODO_LIST:
            Todo.create(name=todo, user=user)

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()


class TodoResourceTestCase(TodoTestCase):

    def test_get_todos(self):
        with test_database(TEST_DB, (Todo, User)):
            self.create_test_todos()
            resp = self.client.get('/api/v1/todos')
            resp_data = json.loads(resp.data.decode())
            self.assertEqual(len(resp_data), 3)

    def test_authorized_add_todo(self):
        with test_database(TEST_DB, (Todo, User)):
            user = User.create_user(**USER_DATA)
            token = user.generate_auth_token().decode('ascii')
            headers = {'Authorization': 'Token {}'.format(token)}

            resp = self.client.post('/api/v1/todos', data={'name': 'Test 1'}, headers=headers)
            resp_data = json.loads(resp.data.decode())
            self.assertEqual(resp.status_code, 201)
            self.assertTrue('Test 1' == resp_data['name'])

    def test_unauthorized_add_todo(self):
        with test_database(TEST_DB, (Todo,)):
            resp = self.client.post('/api/v1/todos', data={'name': 'Test 2'})
            self.assertEqual(resp.status_code, 401)


class UserModelTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app
        self.client = app.test_client()

    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='test_user_{}'.format(i),
                email='test_{}@example.com'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'password'
            )

    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    username='test_user_0',
                    email='test_0@example.com',
                    password='password'
                )

if __name__ == '__main__':
    TEST_DB = SqliteDatabase(':memory:')
    TEST_DB.connect()
    TEST_DB.create_tables([User, Todo], safe=True)
    unittest.main()
