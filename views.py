from redis import Redis
redis = Redis()

from flask import Flask, jsonify, request, g, render_template, redirect, url_for, make_response, flash
from flask_httpauth import HTTPBasicAuth

from models import Base, Item, Category

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import time
import json
import requests
import httplib2

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
auth = HTTPBasicAuth()

CLIENT_ID = 'tempID'#json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

def nav_links():
    return session.query(Category).all()

@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/clientOAuth')
def start():
    return render_template('')

@app.route('/oauth/<provider>', methods = ['GET', 'POST'])
def login(provider):
    auth_code = request.json.get('auth_code')
    print "received auth code %s" % auth_code
    if provider == 'google':
        try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        access_token - credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
        print 'Access Token : %s' % credentials.access_token

        # Get user info
        h = httplib2.Http()
        userinfo_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': credentials.access_token, 'alt':'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        name = data['name']
        picture = data['picture']
        email = data['email']

        # See if user exists. If not, make a new one
        user = session.query(User).filter_by(email=email).first()
        if not user:
            user = User(uesername = name, picture = picture, email =  email)
            session.add(user)
            session.commit()

        # Create and send token back to client
        token = user.generate_auth_token(600)
        return jsonify({'token': token.decode('ascii')})
    elif provider == 'facebook':
        print 'Functionality for Facebook login is still under development' # TODO: Add Facebook login
    else:
        return 'Unrecognized Provider'


@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print 'missing arguments'
        abort(400)

    if session.query(User).filter_by(username=username).first() is not None:
        print 'existing user'
        user = sesion.query(User).filter_by(username=usernmae).first()
        return jsonify({ 'message':'user already exists' }), 200

    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201

@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({ 'username': user.username})

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })


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
    items = session.query(Item).filter_by(category_id=category.id)
    links = nav_links()
    if items:
        print 'this is the if'
        print 'category # ' + str(category.id)
        return render_template('catalog.html', category=category, items=items, links=links)
    else:
        print 'this is the else'
        return render_template('createCatalog.html', category_name=category_name, category=category, items=items, links=links)

@app.route('/<category_name>/<int:item_id>')
def catalogItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name)
    item = session.query(Item).filter_by(id=item_id).first()
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
        return render_template('editCategory.html', category_name=category_name, category=editedCategorycategory, links=nav_links())

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
    category = session.query(Category).filter_by(name=category_name).one()
    editedItem = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = (request.form['name']).lower()
            editedItem.price = request.form['price']
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Item Edited!')
        print 'REQUEST METHOD == POST'
        return redirect(url_for('catalog', category_name=category_name, links=nav_links()))
    else:
        print 'REQUEST METHOD == GET'
        return render_template('editCatalogItem.html', category_name=category_name, category=category, item_id=item_id, item=editedItem, links=nav_links())

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



if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'SUPERSECRETKEY' #''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
