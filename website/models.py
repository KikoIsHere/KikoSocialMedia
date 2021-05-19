from . import db
from flask import current_app as app
from flask_login import UserMixin
from sqlalchemy.sql import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


friend_list = db.Table('friend_list',
    db.Column('user', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend', db.Integer, db.ForeignKey('user.id'))
) 


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    posts = db.relationship('Post')
    friends = db.relationship('User', 
                               secondary=friend_list, 
                               primaryjoin=(friend_list.c.user == id), 
                               secondaryjoin=(friend_list.c.friend == id), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')


    def add_friend(self, user):
        if not self.is_friend(user) and not user.is_friend(self):
            self.friends.append(user)
            user.friends.append(self)
            return self

    def remove_friend(self, user):
        if self.is_friend(user) and user.is_friend(self):
            self.friends.remove(user)
            user.friends.remove(self)
            return self

    def is_friend(self, user):
        return self.friends.filter(friend_list.c.friend == user.id).count() > 0


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column('sender', db.Integer, db.ForeignKey('user.id'))
    receiver = db.Column('reciever', db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean(), default=True)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())

    def accept(self):
        reciever_friend_list = User.query.filter_by(id=self.receiver).first()
        sender_friend_list = User.query.filter_by(id=self.sender).first()
        if reciever_friend_list and sender_friend_list:
            reciever_friend_list.add_friend(sender_friend_list)
            sender_friend_list.add_friend(reciever_friend_list)                
            self.is_active = False
            return self

    def decline(self):
        self.is_active = False
        return self

    def cancel(self):
        self.is_active = False
        return self        

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    data = db.Column(db.String(10000))
    author = db.Column(db.String(256))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    comments = db.relationship('Comment', cascade='save-update, merge, delete')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'))