from asyncio import create_task
from cmath import exp
from re import U
import secrets
from app import db, login
from flask_login import UserMixin 
from datetime import datetime as dt, timedelta
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

pokemon_to_user = db.Table(
    'pokemon_to_user',
    db.Column('pokemon_id', db.Integer, db.ForeignKey('pokemon.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    icon = db.Column(db.Integer)
    token = db.Column(db.String, unique=True, index=True)
    token_exp = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
        )
    pokemon_caught = db.relationship('Pokemon',
    secondary=pokemon_to_user,
    primaryjoin=(pokemon_to_user.c.user_id == id),
    secondaryjoin=(pokemon_to_user.c.pokemon_id == id),
    backref='users')

    def get_token(self, expires_in=86400):
        current_time = dt.utcnow()
        if self.token and self.token_exp > current_time + timedelta(seconds=60):
            return self.token
        self.token=secrets.token_urlsafe(32)
        self.token_exp=current_time + timedelta(seconds=exp)
        self.save()
        return self.token

    def revoke_token(self):
        self.token_exp = dt.utcnow() - timedelta(seconds=60)

    @staticmethod
    def check_token(token):
        u = User.query.filter_by(token=token).first()
        if u and u.token_exp > dt.utcnow():
            return u
        return u


    def __repr__(self):
        return f'<User: {self.email} | {self.id}>'
    
    
    def __str__(self):
        return f'<User: {self.email} | {self.first_name} {self.last_name}>'

    
    def hash_password(self, original_password):
        return generate_password_hash(original_password)

    
    def check_hashed_password(self, login_password):
        return check_password_hash(self.password, login_password)

    
    def save(self):
        db.session.add(self) 
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit() 
    
    def from_dict(self, data):
        self.first_name=data['first_name']
        self.last_name=data['last_name']
        self.email=data['email']
        self.password=self.hash_password(data['password'])
        self.icon=data['icon']

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'created_on': self.created_on,
            'icon': self.icon,
            'token': self.token,
            'is_admin': self.is_admin
        }

    def get_icon_url(self):
        return f"http://avatars.dicebear.com/api/croodles/{self.icon}.svg"

    def is_following(self, user_to_check):
        return self.followed.filter(followers.c.followed_id == user_to_check.id).count() > 0

    def follow(self, user_to_follow):
        if not self.is_following(user_to_follow):
            self.followed.append(user_to_follow)
            db.session.commit()

    def unfollow(self, user_to_unfollow):
        if self.is_following(user_to_unfollow):
            self.followed.remove(user_to_unfollow)
            db.session.commit()

    def followed_posts(self):
        followed = Post.query.join(followers, (Post.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        self_posts =Post.query.filter_by(user_id = self.id)
        all_posts = followed.union(self_posts).order_by(Post.created_on.desc())
        return all_posts

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=dt.utcnow)
    date_updated = db.Column(db.DateTime, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Post: {self.body[:15]} | {self.id}>'

    def __str__(self):
        return f'<Post: {self.body[:15]} | {self.id}>'

    def edit(self, new_body):
        self.body = new_body

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self):
        return {
            'id': self.id,
            'body': self.body,
            'date_created': self.date_created,
            'date_updated': self.date_updated,
            'user_id': self.user_id
        }



class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('pokemon', lazy=True))


    def __repr__(self):
        return f'<Pokemon: {self.name} | {self.id}>'

    def __str__(self):
        return f'<Pokemon: {self.name} | {self.id}>'

    def from_dict(self, data):
        self.name=data['name']
        self.user_id=data['user_id']

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_on': self.created_on,
            'user_id': self.user_id
        }
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_on': self.created_on,
            'user_id': self.user_id
        }

    def save(self):
        db.session.add(self) 
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def save_pokemon(data):
        pokemon = Pokemon(name=data['name'], user_id=data['user_id'])
        pokemon.save()
        return pokemon

    def get_all_pokemon(user_id):
        return Pokemon.query.filter_by(user_id=user_id).all()