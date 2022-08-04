from flask import render_template, request, redirect, url_for, flash
import requests
from app import app
from .forms import LoginForm, RegisterForm, EditProfileForm
from app.forms import CatchPokemon
from .models import *
from flask_login import login_user, login_required, logout_user, current_user


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html.j2')



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        # try:
        new_user_data={
            "first_name":form.first_name.data.title(),
            "last_name":form.last_name.data.title(),
            "email":form.email.data.lower(),
            "password":form.password.data,
            # "icon":form.icon.data
        }
        
        new_user_object = User()

        new_user_object.from_dict(new_user_data)

        new_user_object.save()
        # except:
        #     flash("An Unexpected Error occurred", "danger")
        #     return render_template('register.html.j2', form=form)
        flash("Successfully registered", "success")
        return redirect(url_for('login'))
    return render_template('register.html.j2', form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()
    if request.method == 'POST' and form.validate_on_submit():
        edited_user_data={
                "first_name":form.first_name.data.title(),
                "last_name":form.last_name.data.title(),
                "email":form.email.data.lower(),
                "password":form.password.data,
                "icon":int(form.icon.data) if int(form.icon.data) != 9000 else current_user.icon
            }
        user = User.query.filter_by(email=edited_user_data['email']).first()
        if user and user.email != current_user.email:
            flash('Email is already in use', 'danger')
            return redirect('edit_profile')
        try:
            current_user.from_dict(edited_user_data)
            current_user.save()
            flash("Profile Updated", 'success')
        except:
            flash("Error updating profile", 'danger')
            return redirect('edit_profile')
        return redirect(url_for('index'))
    return render_template('register.html.j2',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        u = User.query.filter_by(email=email).first()
        if u and u.check_hashed_password(password):
            flash('Successfully logged in','success')
            login_user(u)
            return redirect(url_for('index'))
        flash("Incorrect Email/password Combo", "warning")
        return render_template('login.html.j2', form=form)

    return render_template('login.html.j2', form=form)

@app.route('/logout', methods=['GET'])
# @login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'primary')
    return redirect(url_for('index'))


@app.route('/pokemon', methods=['GET', 'POST'])
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