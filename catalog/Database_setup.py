import os

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship,
from sqlalchemy import create_engine
from util import session,dataBaseName,base




def addAndCommit(x):
    if x is not None:
        session.add(x)
        session.commit()
    else:
        print('Null Value )-: at Line 18 in class util.py  [ %s ]' % x)


def deleteAndCommit(x):
    if x is not None:
        session.delete(x)
        session.commit()
    else:
        print('Null Value )-: at Line 26 in class util.py  [ %s ]' % x)


class User(base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(80), nullable=False)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        # serialize self to json format or return as a
        #  map <String, dynamic> in Dart lang or Java (:
        return {
            'name': self.name,
            'id': self.id,
            'email': self.email,
        }


class Markets(base):
    __tablename__ = 'markets'

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    @property
    def serialize(self):
        # serialize self to json format or return as a
        # map <String, dynamic>
        return {
            'name': self.name,
            'id': self.id,
        }


class ItemsInMarket(base):
    __tablename__ = 'items_in_market'

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    market_id = Column(Integer, ForeignKey('markets.id'))
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(String(8), nullable=False)
    market = relationship(Markets)

    @property
    def serialize(self):
        # serialize self to json format ;
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
        }


engine = create_engine(dataBaseName)





base.metadata.create_all(engine)
