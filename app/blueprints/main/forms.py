from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, RadioField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from jinja2.utils import markupsafe
from app.models import  User, Pokemon
from flask_login import current_user




class CatchPokemon(FlaskForm):
    pokemon_name = StringField("What Pokemon would you like to Catch", validators=[DataRequired()])
    submit = SubmitField('Looking for Pokemon')

    def validate_pokemon_name(form, field):
        pokemon = Pokemon.query.filter_by(name = field.data).first()
        if not pokemon:
            return ValidationError('Pokemon not found')
        elif pokemon.user_id == current_user.id:
            return ValidationError('Pokemon is already in your collection')
        # EACH USER SHOULD HAVE THEIR OWN COLLECTION OF UP TO 5 POKEMON
        elif Pokemon.query.filter_by(user_id = current_user.id).count() >= 5:
            return ValidationError('You have reached the maximum number of Pokemon in your collection')

    def catch_pokemon(form, field):
        pokemon = Pokemon.query.filter_by(name = field.data).first()
        pokemon.user_id = current_user.id
        pokemon.save()
        return pokemon
        

  
# Your pokemon form will now catch any searched pokemon
# You will need to:
#         make a table to hold the poke data (add an id field as a primary key)
#         make a table to link the Pokemon to the User they belong too
#         update your db with flask db migrate flask db upgrade

# when they catch a pokemon
#         check to see if the user already collected that pokemon
#         If it hasn't been collected yet by ANY USER then add that pokemon to the data base
     
#         Allow the user to add the pokemon to their collection; if they have less than 5 total pokemon




class PokemonCollection(FlaskForm):
    pokemon_name = StringField("What Pokemon would you like to add to your collection", validators=[DataRequired()])
    submit = SubmitField('Add Pokemon')

    def validate_pokemon_name(form, field):
        pokemon = Pokemon.query.filter_by(name = field.data).first()
        if pokemon:
            return ValidationError('Pokemon is Already in Collection')



        

        