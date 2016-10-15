from flask import Flask, g, jsonify
import config

from resources.todos import todos_api


app = Flask(__name__)
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.route('/')
def my_todos():
    return 'MyTodos'

if __name__ == '__main__':
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)