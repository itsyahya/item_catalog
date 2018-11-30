import os

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy import create_engine

# base = declarative_base()
# # name of the Database
# base.metadata.clear()
# oldDBN = 'sqlite:///markets.db'
#
# path = os.path.abspath(os.getcwd()) + "/markets.db"
#
# newDBN = 'sqlite:///' + path
#
# print(newDBN)
#
#
# # create  engine
# engine = create_engine(newDBN)
# # just import the session (:
# session = scoped_session(sessionmaker(bind=engine))


class User(base):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
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
    __table_args__ = {'extend_existing': True}

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
    __table_args__ = {'extend_existing': True}

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
