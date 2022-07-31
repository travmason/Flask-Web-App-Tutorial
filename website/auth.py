from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Conversation, User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import logging
import os
from .daniel import Bot 

auth = Blueprint('auth', __name__)
bot = Bot()

def open_file(filename):
    document = os.getcwd()+'\\'+filename
    logging.info('open_file document:' + document)
    with open(document, 'r', encoding='utf-8') as infile:
        return infile.read()

def start_conversation(user):
    prompt = "Daniel: Hi, nice to be speaking with you, what's your name?"
    prompt = open_file('website\\prompt_greeting.txt').replace('<<NAME_BLOCK>>', prompt)
    logging.info('prompt: ' + prompt)
    
    logging.info('User:' + str(user))
    conn_id = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.con_id.desc()).first()
    logging.info('conn_id:' + str(conn_id.con_id))
    conn_id.con_id = conn_id.con_id + 1
    new_turn = Conversation(prompt='', session_id=conn_id.con_id, user_id=current_user.id)
    db.session.add(new_turn)
    db.session.commit()

    response = bot.gpt3_completion(str(prompt), temp=0)
    logging.info('Daniel: Hi %s.' % response)
    


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                start_conversation(user)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email not valid.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 6:
            flash('Password must be at least 6 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
