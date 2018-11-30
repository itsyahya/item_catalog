import os

from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash, session as login_session
from sqlalchemy import asc
from Database_setup import Markets, ItemsInMarket, User

import random
import string
# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


from .util import addAndCommit,session,deleteAndCommit,dataBaseName

app = Flask(__name__)

# fetch and read client_secrets file provide by google.
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# login page that use for enable user to login
# for make changes of there markets or items.
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# login page without alert user they must be sign in .
@app.route('/loginHomePage')
def loginHomePage():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('loginHomePage.html', STATE=state)


# this method receive data from google API to manipulate state of the token key
@app.route('/gconnect', methods=['POST'])
def gconnect():  #
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    # some times user my not have name in Google account
    try:
        login_session['username'] = data['name']
    except Exception:
        login_session['username'] = 'no Name'
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    a_user = getUserID(login_session['email'])
    if not a_user:
        newUserID = createUser(login_session)
        login_session['user_id'] = newUserID

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:' \
              ' 150px;-webkit-border-radius: ' \
              '150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    print(login_session)
    return output


# LogOut page to enable user change there account's from one to other one
@app.route('/logout')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    # if the status code is 200 we will clean login_session for next user
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'))
        response.headers['Content-Type'] = 'application/json'
        return response


# Create new User
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'])
    # add object to data base and commit
    addAndCommit(newUser)
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# fetch user object by it is ID ;
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# fetch userID by it is unique email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None


# CURD for Market
@app.route('/')
@app.route('/markets')
def mainPage():
    # show all markets
    # use asc to show markets from A to Z in sequence

    markets = session.query(Markets).order_by(asc(Markets.name))
    return render_template('markets.html',
                           markets=markets, login_session=login_session)


@app.route('/markets/<int:market_id>')
@app.route('/markets/<int:market_id>/items')
def showTargetMarket(market_id):
    # show all items in this market
    market = session.query(Markets).filter_by(id=market_id).one()
    items = session.query(ItemsInMarket).filter_by(market_id=market.id).all()
    try:
        '''if this the first time user visit the site
        the login_session will not have value.So this will fall the site;'''
        if market.user_id != login_session['user_id']:
            return render_template('public_itemsInMarket.html',
                                   market=market, items=items,
                                   login_session=login_session)
    except Exception:
        return render_template('public_itemsInMarket.html',
                               market=market, items=items,
                               login_session=login_session)
    return render_template('itemsInMarket.html',
                           market=market, items=items,
                           login_session=login_session)


@app.route('/markets/edit/<int:market_id>', methods=['POST', 'GET'])
def editMarket(market_id):
    # first check the user is login
    if 'username' not in login_session:
        return redirect('/login')

    # edit target market
    editedMarket = session.query(Markets) \
        .filter_by(id=market_id).one()

    currentUser = getUserInfo(editedMarket.user_id)

    # if the current user is creator will pass this
    # condition other ways he cant make changes
    if currentUser.id != login_session['user_id']:
        return "<script>function aler() {alert('You " \
               "are not authorized to edit this item." \
               "Please create your own item " \
               "in order to edit.');}</script><body onload='aler()'> "

    if request.method == 'POST':
        if request.form['name']:
            editedMarket.name = request.form['name']
            addAndCommit(editedMarket)
            flash('Market Successfully Edited %s'
                  % editedMarket.name)
            return redirect(url_for('mainPage'))
    else:
        return render_template('editMarket.html',
                               market=editedMarket,
                               login_session=login_session)


@app.route('/markets/delete/<int:market_id>', methods=['GET', 'POST'])
def deleteMarket(market_id):
    # first check the user is login
    if 'username' not in login_session:
        return redirect('/login')
    # delete this market
    finalDayOfTheMarket = session.query(Markets) \
        .filter_by(id=market_id).one()

    # if the current user is creator will pass this
    # condition other ways he cant make changes
    if finalDayOfTheMarket.user_id != login_session['user_id']:
        return "<script>function aler() {alert('You are" \
               " not authorized to delete this market." \
               "Please create your own item " \
               "in order to edit.');}</script><body onload='aler()'> "

    if request.method == 'POST':

        deleteAndCommit(finalDayOfTheMarket)
        flash('%s Successfully Deleted'
              % finalDayOfTheMarket.name)

        return redirect(url_for('mainPage'))
    else:
        return render_template('deleteMarket.html',
                               market=finalDayOfTheMarket,
                               login_session=login_session)


@app.route('/markets/new/', methods=['GET', 'POST'])
def newMarket():
    if 'username' not in login_session:
        return redirect('/login')

    # new market
    if request.method == 'POST':
        newMarket = Markets(name=request.form['name'],
                            user_id=login_session['user_id'])
        addAndCommit(newMarket)
        flash('New Market %s Successfully Created'
              % newMarket.name)
        return redirect(url_for('mainPage'))
    else:
        return render_template('newMarket.html',
                               login_session=login_session)


# json for market
@app.route('/markets/json')
def marketJson():
    markets = session.query(Markets).all()
    return jsonify(markets=[x.serialize for x in markets])


# CURD for items in Market
@app.route('/markets/editItem/<int:market_id>/<int:item_id>',
           methods=['GET', 'POST'])
def editItem(market_id, item_id):
    # first check the user is login
    if 'username' not in login_session:
        return redirect('/login')

    # edit an item

    currentMarket = session.query(Markets). \
        filter_by(id=market_id).one()
    targetItem = session.query(ItemsInMarket). \
        filter_by(id=item_id).one()

    if targetItem.user_id != login_session['user_id']:
        return "<script>function aler() {alert('" \
               "You are not authorized to edit this item." \
               "Please create your own item " \
               "in order to edit.');}</script><body onload='aler()'> "

    # if true, we will extract the data by it is name from request object body.
    if request.method == 'POST':
        if request.form['name']:
            targetItem.name = request.form['name']
        if request.form['description']:
            targetItem.description = request.form['description']
        if request.form['price']:
            targetItem.price = request.form['price']
        # save data to database
        addAndCommit(targetItem)
        # make alert to tell user the data was added.
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showTargetMarket',
                                market_id=currentMarket.id))
    else:
        return render_template('editItem.html',
                               item=targetItem,
                               login_session=login_session)


@app.route('/markets/deleteItem/<int:market_id>/<int:item_id>',
           methods=['GET', 'POST'])
def deleteItem(market_id, item_id):
    # first check the user is login
    if 'username' not in login_session:
        return redirect('/login')

    # delete an item
    currentMarket = session.query(Markets). \
        filter_by(id=market_id).one()
    targetItemToDelete = session.query(ItemsInMarket). \
        filter_by(id=item_id).one()

    # if the current user is creator will pass this
    # condition other ways he cant make changes
    if targetItemToDelete.user_id != login_session['user_id']:
        return "<script>function aler() {alert('" \
               "You are not authorized to delete this item." \
               "Please create your own item " \
               "in order to edit.');}</script><body onload='aler()'> "

    if request.method == 'POST':
        deleteAndCommit(targetItemToDelete)
        flash('Item Successfully Deleted')
        return redirect(url_for('showTargetMarket',
                                market_id=currentMarket.id))

    return render_template('deleteItem.html',
                           market=currentMarket,
                           item=targetItemToDelete,
                           login_session=login_session)


@app.route('/markets/newItem/<int:market_id>/', methods=['GET', 'POST'])
def newItem(market_id):
    # first check the user is login
    if 'username' not in login_session:
        return redirect('/login')
    # new item by the target id of the market

    currentMarketID = session.query(Markets). \
        filter_by(id=market_id).one()

    # if the current user is creator will pass this
    # condition other ways he cant make changes
    if currentMarketID.user_id != login_session['user_id']:
        return "<script>function aler() {alert('" \
               "You are not authorized to create new  item for this market." \
               "Please create your own item " \
               "in order to edit.');}</script><body onload='aler()'> "

    if request.method == 'POST':
        newItem = ItemsInMarket(name=request.form['name'],
                                description=request.
                                form['description'],
                                price=request.form['price'],
                                market_id=currentMarketID.id,
                                user_id=currentMarketID.user_id)
        addAndCommit(newItem)
        flash('New Menu %s Item Successfully Created' % newItem.name)

        return redirect(url_for('showTargetMarket',
                                market_id=market_id,
                                login_session=login_session))
    else:
        return render_template('newItem.html',
                               market=currentMarketID,
                               login_session=login_session)


# json for items in Market
@app.route('/markets/items/<int:market_id>/json/')
def itemsInMarket(market_id):
    """
    first make QUERY by this link to get the id of the market

    http://localhost:5000/markets/json

    after that select any id and put it in the link of this route
    like this ---> http://localhost:5000/markets/items/4/json/
    """
    market = session.query(Markets). \
        filter_by(id=market_id).one()
    items = session.query(ItemsInMarket). \
        filter_by(market_id=market.id).all()
    m = {

        'Market': market.name,
        'Items': [x.serialize for x in items],

    }

    return jsonify(m)


@app.route('/markets/users/json')
def userJson():
    users = session.query(User).all()
    return jsonify([x.serialize for x in users])


@app.route('/markets/users/<int:user_id>/json')
def userJsonData(user_id):
    """

    example query
    this -->   http://localhost:5000/markets/users/3/json
    """
    user = session.query(User).filter_by(id=user_id).one()
    market = session.query(Markets).filter_by(user_id=user.id).all()
    items = session.query(ItemsInMarket).filter_by(user_id=user.id).all()

    jsn = {
        'Name ': user.name,
        'Markets': [[x.serialize for x in market],
                    {'Items': [x.serialize for x in items]}],

    }

    return jsonify(jsn)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = dataBaseName
    app.debug = True
    app.run()
