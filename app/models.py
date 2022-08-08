from app import db, login
from flask_login import UserMixin 
from datetime import datetime as dt
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id')),
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, unique=True, index=True)
    password = db.Column(db.String)
    icon = db.Column(db.Integer)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    battles = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, default=dt.utcnow)
    pokemon = db.relationship('Pokemon', backref='master', lazy='dynamic')
    followed = db.relationship('User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
        )

    def __repr__(self): 
        return f'< User: {self.email} | {self.id}>'

    def __str__(self): 
        return f'< User: {self.email} | {self.first_name} {self.first_name}>'

        
    def hash_pass(self, my_password):
        return generate_password_hash(my_password)
        
        
    def check_pass(self, login_pass):
        return check_password_hash(self.password, login_pass)

    def add_win(self):
        self.wins += 1
        db.session.commit()

    def add_loss(self):
        self.losses += 1
        db.session.commit()

    def add_battle(self):
        self.battles += 1
        db.session.commit()
    
    def get_battles(self):
        return self.battles

    def get_wins(self):
        return self.wins

    def get_losses(self):
        return self.losses
        
    def get_battle_record(self):
        return f"{self.wins} - {self.losses} - {self.battles}"
        
    def save(self):
        db.session.add(self) 
        db.session.commit() 

    
    def from_dict(self, data):
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.icon = data['icon']
        self.password = self.hash_pass(data['password'])    

    def get_icon_url(self):
        return f"http://avatars.dicebear.com/api/croodles/{self.icon}.svg"

   
    def is_following(self, user_to_check):
        return self.followed.filter(followers.c.followed_id == user_to_check.id).count()>0

    
    def follow(self, user_to_follow):
        if not self.is_following(user_to_follow):
            self.followed.append(user_to_follow)
            db.session.commit()

    def unfollow(self, user_to_unfollow):
        if self.is_following(user_to_unfollow):
            self.followed.remove(user_to_unfollow)
            db.session.commit()

    
    def followed_posts(self):
        
        followed = Pokemon.query.join(followers, (Pokemon.user_id == followers.c.followed_id)).filter(followers.c.follower_id == self.id)
        self_posts = Pokemon.query.filter_by(user_id = self.id)        
        all_posts = followed.union(self_posts).order_by(Pokemon.date_created.desc())
        return all_posts

   

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Pokemon(db.Model):
    __tablename__ = 'pokemon'

    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ability = db.Column(db.String)
    exp = db.Column(db.String)
    attk = db.Column(db.String)
    hp = db.Column(db.String)
    defense = db.Column(db.String)
    sprite = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    date_caught = db.Column(db.DateTime, default=dt.utcnow)

    def __repr__(self):
        return f"<Pokemon: {self.id} | {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def release(self):
        db.session.delete(self)
        db.session.commit()

    def from_dict(self, poke_dict):
        self.name = poke_dict['Name']
        self.ability = poke_dict['Ability']
        self.exp = poke_dict['BaseExp']
        self.attk = poke_dict['BaseAttk']
        self.hp = poke_dict['BaseHP']
        self.defense = poke_dict['BaseDef']
        self.sprite = poke_dict['Sprite']
        self.user_id = poke_dict['User_id']

    

    def save(self):
        db.session.add(self) 
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    