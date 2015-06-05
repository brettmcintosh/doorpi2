from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt

# import flask
# app = flask.Flask('models')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///alarm.db'
# db = SQLAlchemy(app)

db= SQLAlchemy()


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))

    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def __repr__(self):
        return '<User %r>' % self.username


class NFCCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    key_hash = db.Column(db.String(100))

    def __init__(self, name, key_hash):
        self.name = name
        self.key_hash = key_hash

    def __repr__(self):
        return '<NFC %r>' % self.name

def add_user():
    print('Enter a username...')
    username = input()
    print('Enter a password...')
    password = input()
    print('Enter the password again...')
    password2 = input()

    if password == password2:
        if username != '' and password != '':
            # encrypt the password
            password_hash = sha256_crypt.encrypt(password)

            # add the user to the db
            new_user = User(username, password_hash)
            db.session.add(new_user)
            db.session.commit()
            print('Added %s to the session database.' % new_user.username)

        else:
            print('Username or password was blank. Try again.')
    else:
        print('The passwords do not match. Try again.')


def add_card():
    print('Enter a name for the card...')
    name = input()
    print('Enter the card\'s key...')
    key = input()
    print('Enter the key again...')
    key2 = input()

    if key == key2:
        if name != '' and key != '':
            # encrypt the password
            key_hash = sha256_crypt.encrypt(key)

            # add the user to the db
            new_card = NFCCard(name, key_hash)
            db.session.add(new_card)
            db.session.commit()
            print('Added %s to the key database.' % new_card.name)

        else:
            print('Name or key was blank. Try again.')
    else:
        print('The keys do not match. Try again.')


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        return sha256_crypt.verify(password, user.password_hash)

    return False


def authenticate_nfc(unverified_key):
    all_cards = NFCCard.query.all()
    for card in all_cards:
        if sha256_crypt.verify(unverified_key, card.key_hash):
            return True

    return False