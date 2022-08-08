from . import bp as social
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import User, Pokemon


@social.route('/show_users')
def show_users():
    users=User.query.filter(User.id != current_user.id).all()
    return render_template('show_users.html.j2', users=users)



@social.route('/show_other_users_team/<user_id>')
def show_other_users_pokemon(user_id):
    pokemon=User.query.filter(User.id != current_user.id).all()
    return render_template('show_other_users_team.html.j2', pokemon=pokemon)


@social.route('/follow/<int:id>')
@login_required
def follow(id):
    u = User.query.get(id)
    current_user.follow(u)
    flash(f"You are now following {u.first_name} {u.last_name}", "success")
    return redirect(url_for("social.show_users"))




@social.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    u = User.query.get(id)
    current_user.unfollow(u)
    flash(f"You are no longer following {u.first_name} {u.last_name}", "success")
    return redirect(url_for("social.show_users"))

@social.route('/post/my_posts')
@login_required
def my_posts():
    

    return render_template('my_posts.html.j2', posts=current_user.posts.all())

@social.route('/post/<int:id>')
@login_required
def get_a_post(id):
    post = Pokemon.query.get(id)
    return render_template('single_post.html.j2', post=post, view_all=True)