from flask import (Flask, g, jsonify, render_template,
                   redirect, url_for, flash, request)

from flask_login import (LoginManager, login_user, logout_user,
                         current_user, login_required)

from resources.todos import todos_api
from resources.users import users_api
import config
import forms
import models

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.register_blueprint(todos_api, url_prefix='/api/v1')
app.register_blueprint(users_api, url_prefix='/api/v1')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(userid):
    return models.User.get(id=userid)


@login_manager.token_loader
def load_token(token):
    """
    Flask-Login token_loader callback.
    The token_loader function asks this function to take the token that was
    stored on the users computer process it to check if its valid and then
    return a User Object if its valid or None if its not valid.
    """
    #The Token itself was generated by User.get_auth_token.  So it is up to
    #us to known the format of the token data itself.

    #The Token was encrypted using itsdangerous.URLSafeTimedSerializer which
    #allows us to have a max_age on the token itself.  When the cookie is stored
    #on the users computer it also has a exipry date, but could be changed by
    #the user, so this feature allows us to enforce the exipry date of the token
    #server side and not rely on the users cookie to exipre.
    max_age = app.config["REMEMBER_COOKIE_DURATION"].total_seconds()

    #Decrypt the Security Token, data = [username, hashpass]
    data = models.login_serializer.loads(token, max_age=max_age)

    #Find the User
    user = models.User.get(data[0])

    #Check Password and return user or None
    if user and data[1] == user.password:
        return user
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
