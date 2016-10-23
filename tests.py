import unittest

from playhouse.test_utils import test_database
from peewee import *

import app
from models import User, Todo

TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, Todo], safe=True)

USER_DATA = {
    'username': 'test_user_0',
    'email': 'test_0@example.com',
    'password': 'very_secret'
}


class TodoTestCase(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        app.app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.app.test_client()


class TodoViewTestCase(TodoTestCase):
    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data=USER_DATA)
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users(1)
            rv = self.app.post('/login', data={'username': 'invalid', 'password': 'none'})
            self.assertEqual(rv.status_code, 200)


class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='test_user_{}'.format(i),
                email='test_{}@example.com'.format(i),
                password='very_secret'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
                User.select().get().password,
                'very_secret'
            )

    def test_create_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    username='test_user_0',
                    email='test_0@example.com',
                    password='very_secret'
                )


if __name__ == '__main__':
    unittest.main()
