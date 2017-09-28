from redis import Redis
redis = Redis()

from flask import Flask, jsonify, request, g, render_template, redirect, url_for, make_response, flash
from flask_httpauth import HTTPBasicAuth
from flask import session as login_session

from models import Base, Item, Category

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import time
import random, string
import json
import requests
import httplib2

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Udacity Catalog'

def nav_links():
    return session.query(Category).all()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
        string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)

@app.route('/oauth/<provider>', methods = ['GET', 'POST'])
def login(provider):
    auth_code = request.json.get('auth_code')
    print "received auth code %s" % auth_code
    # Google Login
    if provider == 'google':
        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
        print 'Access Token : %s' % credentials.access_token

        gplus_id = credentials.id_token['sub']
        if result['user_id'] != glpus_id:
            response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        if result['issued_to'] != CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            print "Token's client ID does not match app's."
            response.headers['Content-Type'] = 'application/json'
            return response

        stored_access_token = login_session.get('access_token')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_access_token is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        #Stores the access token in the session for later use.
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['provider'] = 'google'

        # See if user exists. If not, make a new one
        user_id = getUserID(data['email'])
        if not user_id:
            user_id = createUser(login_session)
        login_session['user_id'] = user_id

        # Create and send token back to client
        token = user.generate_auth_token(600)
        return jsonify({'token': token.decode('ascii')})
    # Facebook Login
    elif provider == 'facebook':
        print 'Functionality for Facebook login is still under development' # TODO: Add Facebook login
    else:
        return 'Unrecognized Provider'


@app.route('/')
@app.route('/index')
def showCategories():
    category = session.query(Category).first()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('index.html', category=category, links=nav_links())

@app.route('/catalog/<int:category_id>/JSON', methods=['GET'])
def catalogJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])

@app.route('/catalog/<int:category_id>/item/<int:item_id>/JSON', methods=['GET'])
def catalogItemJSON(category_id, item_id):
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(
        id=item_id).one()
    return jsonify(Item=[item.serialize])

@app.route('/<category_name>')
@app.route('/<category_name>/catalog')
def catalog(category_name):
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        items = session.query(Item).filter_by(category_id=category.id)
    else:
        return 'Not a valid category'
        print 'No category found'
    links = nav_links()
    if items:
        return render_template('catalog.html', category=category, items=items, links=links)
    else:
        print 'this is the else'
        return render_template('createCatalog.html', category_name=category_name, category=category, items=items, links=links)

@app.route('/<category_name>/<int:item_id>')
def catalogItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name)
    if category:
        item = session.query(Item).filter_by(id=item_id).first()
    else:
        return 'not a valid category'
    return render_template('item.html', category=category, item=item, links=nav_links())

@app.route('/newcategory', methods = ['GET', 'POST'])
def newCategory():
    if request.method == 'POST':
        newCategory = Category(name = request.form['name'])
        newCategory.name = (newCategory.name).lower()
        session.add(newCategory)
        session.commit()
        flash('New Category Added!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html', links=nav_links())

@app.route('/<category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    editedCategory = session.query(Category).filter_by(name=category_name).one()

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = (request.form['name']).lower()
        session.add(editedCategory)
        session.commit()
        flash('Category Edited!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('editCategory.html', category_name=category_name, category=editedCategory, links=nav_links())

@app.route('/<category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    categoryToDelete = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
            flash('Category Deleted!')
            return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html', category=categoryToDelete, category_name=category_name, links=nav_links())


@app.route('/<category_name>/new', methods = ['GET', 'POST'])
def newCatalogItem(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        newCatalogItem = Item(name = request.form['name'], price = request.form['price'], description = request.form['description'], category = category)
        session.add(newCatalogItem)
        session.commit()
        flash('New Item Added to Catalog!')
        return redirect(url_for('catalog', category_name = category.name))
    else:
        return render_template('newCatalogItem.html', category_name = category_name, category = category, links=nav_links())

@app.route('/<category_name>/<int:item_id>/edit', methods = ['GET', 'POST'])
def editCatalogItem(category_name, item_id):
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(name=category_name).one()
    links=nav_links()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = (request.form['name']).lower()
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['img_url']:
            editedItem.picture = request.form['img_url']
        session.add(editedItem)
        session.commit()
        flash('Item Edited!')
        print 'REQUEST METHOD == POST'
        return redirect(url_for('catalog', category_name=category_name, links=links))
    else:
        print 'REQUEST METHOD == GET'
        return render_template('editCatalogItem.html', category_name=category_name, category=category, item_id=item_id, item=editedItem, links=links)

@app.route('/<category_name>/<item_id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Deleted!')
        return redirect(url_for('catalog', category_name=category_name))
    else:
        return render_template('deleteCatalogItem.html', category_name=category_name, category=category, item_id=item_id, item=itemToDelete, links=nav_links())

# Helper Functions

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
