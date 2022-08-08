from importlib.machinery import WindowsRegistryFinder
from flask import render_template, request, url_for, flash, redirect
import requests
from .forms import CatchPokemon
from . import bp as main
from app.models import Pokemon, User
from flask_login import login_user, login_required, logout_user, current_user


@main.route('/poke_finder', methods=['GET', 'POST'])
def poke_finder():
    form = CatchPokemon()
    if request.method == 'POST':
        poke_name = form.pokemon_name.data.lower()

        url = f'https://pokeapi.co/api/v2/pokemon/{poke_name}'
        response = requests.get(url)
        if not response.ok:
            error_string = 'An Error has Occured while trying to preform this search'
            return render_template('poke_finder.html.j2', error=error_string, form=form)
        
        pokemon = response.json()
        this_poke = {
            "Name": poke_name.title(),
            "Ability":pokemon["abilities"][0]['ability']['name'],
            "BaseExp":pokemon["base_experience"],
            "BaseAttk":pokemon["stats"][1]['base_stat'],
            "BaseHP":pokemon["stats"][0]['base_stat'],
            "BaseDef":pokemon["stats"][2]['base_stat'],
            "Sprite":pokemon["sprites"]['other']['official-artwork']["front_default"],
            "User_id": current_user.id
        }
        
        print(current_user.pokemon.all())
        return render_template('poke_finder.html.j2', poke=this_poke, name=poke_name.title(), space_in_team=len(current_user.pokemon.all()) < 6,form=form)
    
    return render_template('poke_finder.html.j2', form=form)

@main.route('/catch_pokemon/<poke_name>', methods=['GET', 'POST'])
@login_required
def catch_pokemon(poke_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{poke_name.lower()}'
    response = requests.get(url)
    pokemon = response.json()
    poke_dict = {
        "Name": poke_name.title(),
        "Ability":pokemon["abilities"][0]['ability']['name'],
        "BaseExp":pokemon["base_experience"],
        "BaseAttk":pokemon["stats"][1]['base_stat'],
        "BaseHP":pokemon["stats"][0]['base_stat'],
        "BaseDef":pokemon["stats"][2]['base_stat'],
        "Sprite":pokemon["sprites"]['other']['official-artwork']["front_default"],
        "User_id": current_user.id
    }
    poke_in_team = (True if Pokemon.query.filter_by(user_id=current_user.id, name=poke_dict['Name']).first() else False)
    if poke_in_team:
        flash("You already have this Pokemon!", "warning")
        return redirect(url_for('main.poke_finder'))
    elif len(current_user.pokemon.all()) == 5:
        flash("You're team is already full!", "warning")
        return redirect(url_for('main.poke_finder'))
    else:
        this_poke = Pokemon()
        this_poke.from_dict(poke_dict)
        this_poke.save()
        flash("Pokemon Successfully caught!", "success")
        return redirect(url_for('main.poke_finder'))

@main.route('/my_team')
@login_required
def my_team():
    return render_template('my_team.html.j2', pokemon=current_user.pokemon.all())

@main.route('/show_other_users_team/<int:id>')
@login_required
def show_other_users_team(id):
    user = User.query.get(id)
    return render_template('show_other_users_team.html.j2', pokemon=user.pokemon.all())



#show my team and other users team
@main.route('/battle/<int:id>')
@login_required
def battle(id):
    pokemon=current_user.pokemon
    user = User.query.get(id)
    pokemon1=user.pokemon
    pokemon_total = 0
    pokemon1_total = 0
    for p in pokemon:
        pokemon_total += int(p.attk + p.defense + p.hp + p.exp)
    for p in pokemon1:
        pokemon1_total += int(p.attk + p.defense + p.hp + p.exp)
    if pokemon_total > pokemon1_total:
        winner = current_user
        current_user.add_win()
        user.add_loss()
        current_user.add_battle()
        user.add_battle()
        flash("You Win!", "success")
    elif pokemon_total < pokemon1_total:
        winner = user 
        current_user.add_loss()
        user.add_win()
        current_user.add_battle()
        user.add_battle()
        flash("You Lose!", "danger")    

    return render_template('battle.html.j2', user=user, pokemon=current_user.pokemon.all(), pokemon1=user.pokemon.all(), winner=winner)



@main.route('/release_pokemon/<int:id>')
def release_pokemon(id):
    poke = Pokemon.query.get(id)
    if poke and poke.master.id != current_user.id:
        flash("Pokeball is empty. Try again", 'danger')
        return redirect(url_for('pokemon.index'))
    name = poke.name
    poke.release()
    flash(f"You have returned {name} to the wild!", "success")
    return redirect(url_for('main.my_team'))
    
    
