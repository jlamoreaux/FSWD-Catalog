from flask import (Flask, jsonify, request, g, render_template, redirect,
                   url_for, make_response, flash)
from flask_httpauth import HTTPBasicAuth
from flask import session as login_session

from models import BASE, Item, Category, User, secret_key

from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import time
import datetime
import random
import string
import json
import requests
import httplib2

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Udacity Catalog'
login_button = []
greeting = '0'


@app.before_request
def pass_to_template():
    """
    Passes login/logout button, a greeting and the links to include in the
    navigation bar to rendered templates
    """
    g.greeting, g.login_button = loggedInOrOut()
    g.links = nav_links()
    print 'pass_to_template complete'


@app.route('/login')
def showLogin():
    """Renders Login page"""
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, CLIENT_ID=CLIENT_ID)


@app.route('/oauth/<provider>', methods=['GET', 'POST'])
def login(provider):
    """Oauth Procedure"""

    if provider == 'google':
        #Google Login

        if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter.'),
                                     401)
            response.headers['Content-Type'] = 'application/json'
            return response
        # Obtain authorization code
        code = request.data
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json',
                                                 scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
        except FlowExchangeError:
            response = make_response(
                json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."),
                401)
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
            response = make_response(
                json.dumps('Current user is already connected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Stores the access token in the session for later use.
        login_session['access_token'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']
        login_session['provider'] = 'google'

        # See if user exists. If not, make a new one
        user = getUser(data['email'])
        if not user:
            user = createUser(login_session)
        login_session['user_id'] = user.id

        # Create and send token back to client
        token = user.generate_auth_token(600)
        return jsonify({'token': token.decode('ascii')})

    elif provider == 'facebook':
        # Facebook Login

        if request.args.get('state') != login_session['state']:
            response = make_response(
                json.dumps('Invalid state parameter.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        access_token = request.data
        print "access token: %s" % access_token

        app_id = json.loads(
            open('fb_client_secrets.json', 'r').read())['web']['app_id']
        app_secret = json.loads(
            open('fb_client_secrets.json', 'r').read())['web']['app_secret']
        url = ('https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s') % (app_id, app_secret, access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        token = result.split(',')[0].split(':')[1].replace('"', '')
        url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        for i in data:
            print i

        # Store user data in login_session
        login_session['provider'] = 'facebook'
        login_session['username'] = data["name"]
        login_session['email'] = data["email"]
        login_session['facebook_id'] = data["id"]
        login_session['access_token'] = token

        # Get user picture
        url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        login_session['picture'] = data["data"]["url"]

        # Check to see if user exists
        user_id = getUser(login_session['email'])
        if not user_id:
            user_id = createUser(login_session)
        login_session['user_id'] = user_id

        # Successful login will prompt a greeting
        output = ''
        output += '<h3>Welcome, '
        output += login_session['username']
        output += '!</h3>'
        output += '<img src="'
        output += login_session['picture']
        output += ''' " style = "width: 150px; height: 150px;border-radius:
        75px;-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '''
        flash("Hello %s!" % login_session['username'])
        print "done!"
        return output
    else:
        return 'Unrecognized Provider'


@app.route('/disconnect/<provider>')
def disconnect(provider):
    """Logout Procedure"""

    if provider == 'google':
        # Google Logout
        access_token = login_session.get('access_token')
        if access_token is None:
            print 'Access Token is None'
            response = make_response(
                json.dumps('Current user not connected.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response
        print 'In disconnect access token is %s', access_token
        print 'User name is: '
        print login_session['username']
        url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
               % login_session['access_token'])
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        print 'result is '
        print result
        if result['status'] == '200':
            del login_session['access_token']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['provider']
            flash('Successfully disconnected')
            return redirect('/index')
        else:
            response = make_response(
                json.dumps('Failed to revoke token for given user.'), 400)
            response.headers['Content-Type'] = 'application/json'

    elif provider == 'facebook':
        # Facebook Logout
        facebook_id = login_session['facebook_id']
        access_token = login_session['access_token']
        url = ('https://graph.facebook.com/%s/permissions?access_token=%s'
               % (facebook_id, access_token))
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        del login_session['access_token']
        del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash('Successfully disconnected')
        return redirect('/')


@app.route('/log')
def connectionRedirect():
    """Routes to login or logout, depending on login state"""

    if 'username' not in login_session:
        return redirect('/login')
    elif login_session['provider'] == 'facebook':
        return redirect('/disconnect/facebook')
    elif login_session['provider'] == 'google':
        return redirect('/disconnect/google')
    else:
        return 'Unrecognized provider'


@app.route('/')
@app.route('/index')
def showCategories():
    """Routes to homepage"""
    category = session.query(Category).first()
    items = session.query(Item).order_by('date_added').all()
    if g.links:
        print g.links
    for i in items:
        print i.date_added
    return render_template('index.html', category=category, items=items)


@app.route('/catalog/JSON', methods=['GET'])
def categoriesJSON():
    """Returns a JSON object containing all categories"""
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

@app.route('/catalog/<category_name>/JSON', methods=['GET'])
def catalogJSON(category_name):
    """Returns a JSON object containing all items in the category"""
    category = session.query(Category).filter_by(name=category_name).first()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<int:item_id>/JSON', methods=['GET'])
def catalogItemJSON(category_name, item_id):
    """Returns a JSON object for a specific item"""
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        id=item_id).one()
    return jsonify(Item=[item.serialize])


@app.route('/<category_name>')
@app.route('/<category_name>/catalog')
def catalog(category_name):
    """Routes to catalog for a specific category"""
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        items = session.query(Item).filter_by(category_id=category.id)
    else:
        return 'Not a valid category'
    if items:
        return render_template('catalog.html', category=category, items=items)
    else:
        return render_template(
            'createCatalog.html', category_name=category_name,
            category=category, items=items)


@app.route('/<category_name>/<int:item_id>')
def catalogItem(category_name, item_id):
    """Routes to a specific item in a catalog"""
    category = session.query(Category).filter_by(name=category_name).one()
    if category:
        item = session.query(Item).filter_by(id=item_id).first()
    else:
        return 'not a valid category'
    return render_template('item.html', category=category, item=item)


@app.route('/newcategory', methods=['GET', 'POST'])
def newCategory():
    """Authorized users can create new categories"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'])
        newCategory.name = (newCategory.name).lower()
        session.add(newCategory)
        session.commit()
        flash('New Category Added!')
        return redirect(url_for('showCategories'))
    else:
        return render_template('newCategory.html')


@app.route('/<category_name>/edit', methods=['GET', 'POST'])
def editCategory(category_name):
    """Authorized users can edit categories"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    editedCategory = (session.query(Category)
                      .filter_by(name=category_name).first())
    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = (request.form['name']).lower()
        session.add(editedCategory)
        session.commit()
        flash('Category Edited!')
        return redirect(url_for('showCategories'))
    else:
        return render_template(
            'editCategory.html',
            category_name=category_name,
            category=editedCategory)


@app.route('/<category_name>/delete', methods=['GET', 'POST'])
def deleteCategory(category_name):
    """Authorized users can delete categories"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    categoryToDelete = (session.query(Category)
                        .filter_by(name=category_name).first())
    if request.method == 'POST':
            session.delete(categoryToDelete)
            session.commit()
            flash('Category Deleted!')
            return redirect(url_for('showCategories'))
    else:
        return render_template(
            'deleteCategory.html',
            category=categoryToDelete,
            category_name=category_name)


@app.route('/<category_name>/new', methods=['GET', 'POST'])
def newCatalogItem(category_name):
    """Authorized users can add new items to catalog"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        newCatalogItem = Item(
            name=request.form['name'],
            price=request.form['price'],
            description=request.form['description'],
            category=category)
        session.add(newCatalogItem)
        session.commit()
        flash('New Item Added to Catalog!')
        return redirect(url_for('catalog', category_name=category.name))
    else:
        return render_template(
            'newCatalogItem.html',
            category_name=category_name,
            category=category)


@app.route('/<category_name>/<int:item_id>/edit', methods=['GET', 'POST'])
def editCatalogItem(category_name, item_id):
    """Authorized users can edit items in a catalog"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(name=category_name).one()
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
        return redirect(url_for('catalog', category_name=category_name))
    else:
        print 'REQUEST METHOD == GET'
        return render_template(
            'editCatalogItem.html',
            category_name=category_name,
            category=category,
            item_id=item_id,
            item=editedItem)


@app.route('/<category_name>/<item_id>/delete', methods=['GET', 'POST'])
def deleteCatalogItem(category_name, item_id):
    """Authorized users can delete items in a catalog"""
    # Check to see if user is logged in
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Item Deleted!')
        return redirect(url_for('catalog', category_name=category_name))
    else:
        return render_template(
            'deleteCatalogItem.html',
            category_name=category_name,
            category=category,
            item_id=item_id,
            item=itemToDelete)


# Helper Functions
def nav_links():
    """Creates a list of categories for navigation bar"""
    return session.query(Category).all()


def loggedInOrOut():
    """Checks to see if user is logged in or not"""
    if 'username' in login_session:
        greeting = 'Hi ' + User.username + '!'
        login_button = 'Logout'
    else:
        greeting = ' '
        login_button = 'Login'
    print 'logInOrOut function complete'
    return greeting, login_button


def createUser(login_session):
    """Registers new users in the database"""
    newUser = User(
            username=login_session['username'],
            email=login_session['email'],
            picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user


def getUser(email):
    """
    Queries database for user information
    If user exists, will return that user's data
    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user
    except:
        return None


if __name__ == '__main__':
    app.config['SECRET_KEY'] = secret_key
    app.run(host='0.0.0.0', port=8000)
