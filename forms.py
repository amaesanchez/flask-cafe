"""Forms for Flask Cafe."""

from flask_wtf import FlaskForm
# from wtforms_alchemy import model_form_factory
from wtforms import StringField, SelectField, TextAreaField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length



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
