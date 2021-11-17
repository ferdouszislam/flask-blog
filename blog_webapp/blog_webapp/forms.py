from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from blog_webapp.models import User
from flask_login import current_user

# using flask_wtf all forms can be implemented with python classes
# which can be referenced from html templates


class RegistrationForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField(label="Signup")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Sorry, username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Sorry, email already exists.')


class LoginForm(FlaskForm):
    email = StringField(label='Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label="Login")


class UpdateProfileForm(FlaskForm):
    username = StringField(label='Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    # todo: update password will be implemented through email

    profile_picture = FileField('Update profile picture',
                                validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField(label="Update")

    def validate_username(self, username):
        if current_user.username == username.data:
            return   # data was not updated

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Sorry, username already exists.')

    def validate_email(self, email):
        if current_user.email == email.data:
            return   # data was not updated

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Sorry, email already exists.')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')
