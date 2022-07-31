from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Conversation(db.Model):
    __tablename__ = 'conversations'
    con_id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer)
    prompt = db.Column(db.String(100000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    conversations = db.relationship('Conversation')

class Prompt(db.Model):
    __tablename__ = 'prompt'
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.String(1000))
