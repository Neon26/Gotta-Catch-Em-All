from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from jinja2.utils import markupsafe


class CatchPokemon(FlaskForm):
    pokemon_name = StringField("What Pokemon would you like to Catch", validators=[DataRequired()])
    submit = SubmitField('Looking for Pokemon')