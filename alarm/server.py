from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import json
import logging

from alarm import Alarm
from models import db, authenticate_user
import settings


logging.basicConfig(filename=settings.LOG_FILE_PATH,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    level=logging.INFO)

app = Flask('server')
app.secret_key = settings.FLASK_SESSION_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alarm.db'
db.init_app(app)

alarm = Alarm()


def get_alarm_status():
    alarm_data = {'status': alarm.status,
                  'triggered': alarm.is_triggered,
                  'entry_time': alarm.entry_time}
    return json.dumps(alarm_data)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # print('session user: %s' % session.get('username'))
        if not session.get('username'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login/', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        if session.get('username'):
            return redirect(url_for('index'))
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if authenticate_user(username, password):
            # add username to session and redirect to index
            # session.permanent = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            # add error and reload login page
            error = 'Username or Password was incorrect.'
            return render_template('login.html', error=error)


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():

    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':

        request_data = request.get_json()
        action = request_data.get('action')
        logging.info('Received HTTP request: %s.', action)

        if action == 'ARM':
            logging.debug('Quickarming.')
            alarm.quickarm()

        if action == 'DISARM':
            logging.debug('Quickdisarming.')
            alarm.quickdisarm()

        return get_alarm_status()


@app.route('/api/nfc/', methods=['POST'])
def nfc():

    if request.method == 'POST':
        data = request.get_json()
        key = str(data.get('nfcid'))
        logging.info('Received HTTP NFC request: %s.', key)
        alarm.receive_nfc_message(key)
        return get_alarm_status()


@app.route('/api/status/')
@login_required
def api():
    return get_alarm_status()


if __name__ == '__main__':
    logging.info('Starting server...')
    app.run('0.0.0.0', settings.HTTP_SERVER_PORT)
    # app.run('0.0.0.0', settings.HTTP_SERVER_PORT, debug=True)