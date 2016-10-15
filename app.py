from flask import Flask, g, jsonify
import config

app = Flask(__name__)


@app.route('/')
def my_todos():
    return 'MyTodos'

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)