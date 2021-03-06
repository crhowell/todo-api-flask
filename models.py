import datetime

from flask_login import UserMixin
from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired, URLSafeTimedSerializer)
from peewee import *

import config



HASHER = PasswordHasher()

login_serializer = URLSafeTimedSerializer(config.SECRET_KEY)

DATABASE = config.DATABASE


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()

    class Meta:
        database = DATABASE

    def __str__(self):
        return self.username

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where(
                (cls.email == email) | (cls.username**username)
            ).get()
        except cls.DoesNotExist:
            user = cls(username=username, email=email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            raise ValueError("User with that email or username already exists")

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(id=data['id'])
            return user

    @staticmethod
    def set_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    def get_auth_token(self):
        data = [str(self.id), self.password]
        return login_serializer.dumps(data)

    def generate_auth_token(self, expires=3600):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id': self.id})


class Todo(Model):
    name = CharField()
    completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.datetime.now)
    modified_on = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(User, related_name='todo_set')

    class Meta:
        database = DATABASE


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Todo], safe=True)
    DATABASE.close()
