from flask import (Flask, g, jsonify, render_template,
                   redirect, url_for, flash, request)

from flask_login import (LoginManager, login_user, logout_user,
                         current_user, login_required)

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
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash('You are now registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('login'))
    return render_template('forms/register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash('Your username or password does not match', 'error')
        else:
            if user and user.verify_password(form.password.data):
                login_user(user)
                flash('You have been logged in!', 'success')
                return redirect(url_for('my_todos'))
            else:
                flash('Your username or password does not match!', 'error')
    return render_template('forms/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('my_todos'))


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
