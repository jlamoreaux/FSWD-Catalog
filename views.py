from redis import Redis
redis = Redis()

from flask import Flask, jsonify, request, g, render_template, redirect, url_for
from models import Base, Item, Category

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import time
import json

engine = create_engine('sqlite:///catalog.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)

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
    output = ''
    #output += category
    output += '</br>'
    for i in items:
        output += 'Item:'
        output += '</br>'
        output += i.name
        output += '</br>'
        output += i.price
        output += '</br>'
        output += i.description
        output += "</br>"
        output += str(i.category_id)
        output += '</br></br>'
    return output



if __name__ == '__main__':
    app.secret_key = 'super_secret_key' # TODO: Make an actual secret_key
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
