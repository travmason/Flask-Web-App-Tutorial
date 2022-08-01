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
        message = 'Human: ' + request.form.get('note')
        logging.info('message: ' + message)
        conversation_text = list()

        if len(message) < 1:
            flash('Did you mean to say something?', category='error')
        else:
            conversation = Conversation.query.filter_by(user_id=current_user.id).order_by(Conversation.con_id.desc()).first()
            if conversation:
                logging.info('session_id:' + str(conversation.session_id))
            conversation.prompt = conversation.prompt + '\n' + message
            conversation.user_id=current_user.id
            new_note = Note(data=message, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()

            conversation_text.append(conversation.prompt)
            text_block = '\n'.join(conversation_text)
            prompt = open_file('website/prompt_init.txt').replace('<<BLOCK>>', text_block)
            prompt = prompt + '\nDaniel:'
            response = bot.gpt3_completion(prompt)
            display_response = 'Daniel: ' + response
            conversation.prompt = conversation.prompt + '\nDaniel: ' + response
            new_note = Note(data=display_response, user_id=current_user.id)
            db.session.add(new_note)

            db.session.commit()

            # flash('Note added!', category='success')

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

@views.route('/conversations', methods=['GET', 'POST'])
@login_required
def conversations():
    data = Conversation.query.all()
    return render_template("show.html", conversations = data)