"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
# from wtforms_alchemy import model_form_factory
from wtforms import StringField, SelectField, TextAreaField, PasswordField, EmailField, URLField
from wtforms.validators import InputRequired, Email, Length, Optional, URL



class CafeForm(FlaskForm):
    """ Form for adding cafes """
    # class Meta:
    #     model=Cafe

    name = StringField('Cafe Name',
        validators=[InputRequired()])

    description = TextAreaField('Description',
        validators=[InputRequired()])

    url = StringField('Website',
        validators=[InputRequired()])

    address = StringField('Address',
        validators=[InputRequired()])

    city_code = SelectField('City',
        validators=[InputRequired()])

    image_url = StringField('Image URL')

class SignupForm(FlaskForm):
    """ Form for creating a new user """

    username = StringField('Username',
        validators=[InputRequired()])

    first_name = StringField('First Name',
        validators=[InputRequired()])

    last_name = StringField('Last Name',
        validators=[InputRequired()])

    description = TextAreaField('About You')

    email = EmailField('Email',
        validators=[InputRequired(), Email()])

    password = PasswordField('Password',
        validators=[InputRequired(), Length(min=6)])

    image_url = URLField('Profile Image',
        validators=[Optional(), URL()])

class LoginForm(FlaskForm):
    """ Form for logging in for an existing user """

    username = StringField('Username',
        validators=[InputRequired()])

    password = PasswordField('Password',
        validators=[InputRequired(), Length(min=6)])
