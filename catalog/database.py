import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

path = os.path.abspath(os.getcwd()) + "/markets.db"

dataBaseName = 'sqlite:///' + path
app.secret_key = 'x'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = dataBaseName

db = SQLAlchemy(app)


class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)

    @property
    def serialize(self):
        # serialize self to json format or return as a
        #  map <String, dynamic> in Dart lang or Java (:
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
        }


class Markets(db.Model):
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    @property
    def serialize(self):
        # serialize self to json format or return as a
        # map <String, dynamic>
        return {
            'name': self.name,
            'id': self.id,
        }


class ItemsInMarket(db.Model):
    # __tablename__ = db.Table('items_in_market')
    __table_args__ = {'extend_existing': True}
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)
    market_id = db.Column(db.Integer, db.ForeignKey('markets.id'))
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(250))
    price = db.Column(db.String(8), nullable=False)
    market = db.relationship(Markets)

    @property
    def serialize(self):
        # serialize self to json format ;
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }


def addAndCommit(x):
    if x is not None:
        db.session.add(x)
        db.session.commit()
    else:
        print('Null Value )-: at Line 18 in class util.py  [ %s ]' % x)


def deleteAndCommit(x):
    if x is not None:
        db.session.delete(x)
        db.session.commit()
    else:
        print('Null Value )-: at Line 26 in class util.py  [ %s ]' % x)


db.create_all()
