from redis import Redis
redis = Redis()

from flask import Flask, jsonify, request, g, render_template, redirect, url_for, make_response
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

@app.route('/oauth/<provider>', methods = ['POST'])
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
def index():
    category = session.query(Category).first()
    items = session.query(Item).filter_by(category_id=category.id)
    output = ''
    for i in items:
        output += 'Item:'
        output += '</br>'
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += '</br></br>'
    return output

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

#@app.route('/catalog/<int:category_id>/')
@app.route('/<category_name>')
def catalog(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id)
    return render_template('catalog.html', category=category, items=items)

@app.route('/<category_name>/<item_id>')
def catalogItem(category_name, item_id):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('item.html', category=category, item=item)



if __name__ == '__main__':
    app.config['SECRET_KEY'] = 'SUPERSECRETKEY' #''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
