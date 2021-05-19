from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User, db
from . import mail
from flask import current_app as app
from .forms import RegisterForm, LoginForm, RequestResetForm, ResetPasswordForm
from flask_login import login_user, logout_user,  login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    user = User.query.filter_by(username=form.username.data).first()
    if current_user.is_authenticated:
        return redirect('/')
    if form.validate_on_submit():
        if not check_password_hash(user.password, form.password.data):
            print('incorrect password, try again.')
            return render_template('login.html', form=form)
        login_user(user, remember=True)
        print('logged in!')
        return redirect(url_for('views.home'))
    print(form.errors)
    return render_template('login.html', form=form)


@auth.route('/signup', methods=['POST','GET'])
def signup():
    form = RegisterForm()
    if current_user.is_authenticated:
        return redirect('/')
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=generate_password_hash(form.password.data, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        print('Account created!')
        return redirect(url_for('auth.login'))
    print(form.errors)
    return render_template('signup.html', form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

# To Fix sender
def sendResetEmail(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
    {url_for('auth.resetPassword', token=token, _external=True)}
    If you did not make this request then simply ignore this email and no changes will be made.
    '''
    mail.send(msg)


@auth.route("/resetPassword", methods=['GET', 'POST'])
def resetRequest():
    if current_user.is_authenticated:
        return redirect(url_for('view.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        sendResetEmail(user)
        return redirect(url_for('auth.login'))
    return render_template('resetRequest.html', title='Reset Password', form=form)


@auth.route("/resetPassword/<token>", methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('view.home'))
    user = User.verify_reset_token(token)
    if user is None:
        return redirect(url_for('auth.resetRequest'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(form.password.data, method='sha256')
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('resetPassword.html', title='Reset Password', form=form)
