from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from .models import Conversation
from . import db
from . import bot
from .auth import open_file
import json
import logging

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')
        message = request.form.get('note')
        conversation_text = list()

        if len(note) < 1:
            flash('Did you mean to say something?', category='error')
        else:
            conn_id = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.con_id.desc()).first()
            logging.info('conn_id:' + str(conn_id.con_id))
            new_turn = Conversation(prompt=message, session_id=conn_id.con_id, user_id=current_user.id)
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.add(new_turn)
            db.session.commit()

            conversation_text.append('Human: %s' % message)
            text_block = '\n'.join(conversation_text)
            prompt = open_file('website\\prompt_init.txt').replace('<<BLOCK>>', text_block)
            prompt = prompt + '\nDaniel:'
            response = bot.gpt3_completion(prompt)
            logging.info('Daniel: ' + response)
            conversation_text.append('Daniel: %s' % response)

            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
