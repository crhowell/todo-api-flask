import os

from peewee import SqliteDatabase


basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000
SECRET_KEY = 'GWK~M$F2"|[|i|,KEJWxvA5~JQN!}fUz>|&h`>g.K2/p)%t3%4P:tuR6G6A'
DEFAULT_RATE = "100/hour"

DATABASE = SqliteDatabase('todos.sqlite')
