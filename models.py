import random
import string
import datetime
from sqlalchemy import(
    Column, ForeignKey, Integer, String, create_engine, DateTime)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


BASE = declarative_base()
secret_key = ''.join(
    random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(BASE):
    """Defines 'User' Table"""
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)

    def generate_auth_token(self, expiration=600):
        """Creates token to send to client"""
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})


class Category(BASE):
    """Defines 'Category' Table"""
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)


    @property
    def serialize(self):
        """Returns data in easily serializable format"""
        return {
            'name': self.name,
            'id':   self.id,
        }


class Item(BASE):
    """Defines 'Item' Table"""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    picture = Column(String(250))
    description = Column(String(400))
    price = Column(String)
    date_added = Column(DateTime)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

    @property
    def serialize(self):
        """Returns object in an easily serializable format"""
        return {
            'name':         self.name,
            'id':           self.id,
            'picture':      self.picture,
            'price':        self.price,
            'description':  self.description,
        }


ENGINE = create_engine('sqlite:///catalog.db')

BASE.metadata.create_all(ENGINE)
