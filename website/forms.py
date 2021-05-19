from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from wtforms.widgets import TextArea
from .models import User
import email_validator


class RegisterForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    email = StringField(label='Email', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    password2 = PasswordField(label='Confirm Password', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('User already exists!')

    def validate_email(self, email):
        email = User.query.filter_by(username=email.data).first()
        if email:
            raise ValidationError('Email already exists!')   


class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if not user:
            raise ValidationError("User doesnt't exist")    


class AddPostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    content = StringField(label='Content', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(label='Create Post')


class EditPostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    content = StringField(label='Content', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(label='Edit Post')


class RequestResetForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    submit = SubmitField(label='Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class AddCommentForm(FlaskForm):
    commentField = StringField(label='Comment', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(label='Create comment')

class EditCommentForm(FlaskForm):
    commentField = StringField(label='Comment', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField(label='Edit comment')