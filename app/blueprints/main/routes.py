from flask import render_template, request, abort, make_response
import requests
from .forms import CatchPokemon
from . import bp as main
from app.models import Pokemon


@main.route('/pokemon', methods=['GET', 'POST'])
# @login_required
def pokemon():
    form = CatchPokemon()
    if request.method =='POST':
        pokemon_name = form.pokemon_name.data.lower()
        url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/'
        response = requests.get(url)
        if not response.ok:
            error_string = "That pokemon isnt in our database yet! Try again, or check your spelling!"
            return render_template('pokemon.html.j2', error=error_string,form=form)
        data = response.json()
        for pokemon in data:
            poke_dict={}
            poke_dict={
                "name": data['name'].title(),
                "ability":data['abilities'][0]["ability"]["name"],
                "base experiance":data['base_experience'],
                "photo":data['sprites']['other']['home']["front_default"],
                "attack base stat": data['stats'][1]['base_stat'],
                "hp base stat":data['stats'][0]['base_stat'],
                "defense stat":data['stats'][2]["base_stat"]
            }
            
        return render_template('pokemon.html.j2', pokemon=poke_dict, form=form) 
    return render_template('pokemon.html.j2', form=form)

@main.post('/pokemon')
def post_pokemon():
    pokemon_dict = request.get_json()
    if not all(key in pokemon_dict for key in ['name', 'ability', 'base experiance', 'photo', 'attack base stat', 'hp base stat', 'defense stat']):
        abort(400)
    pokemon = Pokemon()
    pokemon.from_dict(pokemon_dict)
    pokemon.save()
    return make_response(f'{pokemon_dict["name"]} has been added to the database', 200)

@main.get('/pokemon')
def get_pokemon():
    pokemon = Pokemon.query.all()
    pokemon_dicts=[pokemon.to_dict() for pokemon in pokemon]
    return make_response({"pokemon": pokemon_dicts}, 200)

@main.get('/pokemon/<int:pokemon_id>')
def get_pokemon_by_id(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        abort(404)
    pokemon_dict = pokemon.to_dict()
    return make_response({"pokemon": pokemon_dict}, 200)

@main.put('/pokemon/<int:pokemon_id>')
def put_pokemon(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        abort(404)
    pokemon_dict = request.get_json()
    if not all(key in pokemon_dict for key in ['name', 'ability', 'base experiance', 'photo', 'attack base stat', 'hp base stat', 'defense stat']):
        abort(400)
    pokemon.from_dict(pokemon_dict)
    pokemon.save()
    return make_response({"pokemon": pokemon_dict}, 200)

@main.delete('/pokemon/<int:pokemon_id>')
def delete_pokemon(pokemon_id):
    pokemon = Pokemon.query.get(pokemon_id)
    if not pokemon:
        abort(404)
    pokemon.delete()
    return make_response({"message": "pokemon deleted"}, 200)
    
    
