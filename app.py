from flask import (Flask, g, jsonify, render_template,
                   redirect, url_for, flash)
from flask.ext.login import LoginManager
import config
from auth import auth
from resources.todos import todos_api
from resources.users import users_api

import forms
import models

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(todos_api, url_prefix='/api/v1')
app.register_blueprint(users_api, url_prefix='/api/v1')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id==userid)
    except models.DoesNotExist:
        return None


@app.route('/login', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('You are now registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('my_todos'))
    return render_template('forms/register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    pass


@app.route('/logout', methods=('GET',))
def logout():
    pass


@app.route('/')
def my_todos():
    return render_template('index.html')


@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='admin',
            email='admin@example.com',
            password='p4ssw0rd'
        )
    except ValueError:
        pass
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
