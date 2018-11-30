# import os
#
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session
# from sqlalchemy.ext.declarative import declarative_base
#
# base = declarative_base()
# # name of the Database
# base.metadata.clear()
# oldDataBaseName = 'sqlite:///markets.db'
#
#
# path = os.path.abspath(os.getcwd())+"/markets.db"
#
# dataBaseName = 'sqlite:///'+path
#
# print(dataBaseName)
#
#
# x = os.environ.get('sqlite:///markets.db')
#
#
#
# # create  engine
# engine = create_engine(dataBaseName)
# # just import the session (:
# session = scoped_session(sessionmaker(bind=engine))
#
#
# def addAndCommit(x):
#     if x is not None:
#         session.add(x)
#         session.commit()
#     else:
#         print('Null Value )-: at Line 18 in class util.py  [ %s ]' % x)
#
#
# def deleteAndCommit(x):
#     if x is not None:
#         session.delete(x)
#         session.commit()
#     else:
#         print('Null Value )-: at Line 26 in class util.py  [ %s ]' % x)
