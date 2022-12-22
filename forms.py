"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length

class AddCafe(FlaskForm):
    """ Form for adding cafes """

    name = StringField('Cafe Name',
        validators=[InputRequired()])

    description = StringField('Description',
        validators=[InputRequired()])

    url = StringField('Website',
        validators=[InputRequired()])

    address = StringField('Address',
        validators=[InputRequired()])

    city_code = StringField('City Code',
        validators=[InputRequired()])

    image_url = StringField('Image URL',
        validators=[InputRequired()])

class EditCafe(FlaskForm):
    """ Form for editing cafes """

    name = StringField('Cafe Name',
        validators=[InputRequired()])

    description = StringField('Description',
        validators=[InputRequired()])

    url = StringField('Website',
        validators=[InputRequired()])

    address = StringField('Address',
        validators=[InputRequired()])

    city_code = StringField('City Code',
        validators=[InputRequired()])

    image_url = StringField('Image URL',
        validators=[InputRequired()])
