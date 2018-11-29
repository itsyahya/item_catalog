import os

from Database_setup import User, Markets, ItemsInMarket
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

base = declarative_base()
# name of the Database
oldDataBaseName = 'sqlite:///markets.db'


path = os.path.abspath(os.getcwd())+"/markets.db"

dataBaseName = 'sqlite:///'+path

print(dataBaseName)


x = os.environ.get('sqlite:///markets.db')



# create  engine
engine = create_engine(oldDataBaseName)
# just import the session (:
session = scoped_session(sessionmaker(bind=engine))


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




# Create dummy user
u1 = User(name="YahYa", email="a@a.com")
addAndCommit(u1)

# Create market
m1 = Markets(user_id=1, name="Apple")
addAndCommit(m1)

# Create some items
i1 = ItemsInMarket(user=u1, name='Iphone X',
                   description='256 gigs',
                   price='3.99', market=m1)
addAndCommit(i1)
i1 = ItemsInMarket(user=u1, name='Iphone SE',
                   description='20 gigs',
                   price='1.99', market=m1)
addAndCommit(i1)
i1 = ItemsInMarket(user=u1, name='Iphone 8',
                   description='128 gigs',
                   price='2.49', market=m1)
addAndCommit(i1)

# Create dummy user
u1 = User(name="Nora", email="nora@nora.com")
addAndCommit(u1)

# Create market
m1 = Markets(user_id=1, name="Samsung")
addAndCommit(m1)

# Create some items
i1 = ItemsInMarket(user=u1, name='Galaxy s8',
                   description='256 gigs',
                   price='3.99', market=m1)
addAndCommit(i1)
i1 = ItemsInMarket(user=u1, name='note 9',
                   description='20 gigs',
                   price='1.99', market=m1)
addAndCommit(i1)
i1 = ItemsInMarket(user=u1, name='Iphone 8',
                   description='128 gigs',
                   price='2.49', market=m1)
addAndCommit(i1)

print("added menu items!")
