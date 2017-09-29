from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import random, string

BASE = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

class Category(BASE):
    """
    Defines 'Category' Table
    """
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        '''Returns data in easily serializable format'''
        return {
            'name': self.name,
            'id':   self.id,
        }


class Item(BASE):
    """
    Defines 'Item' Table
    """
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    picture = Column(String(250))
    description = Column(String(400))
    price = Column(String)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        '''Returns object in an easily serializable format'''
        return {
            'name':         self.name,
            'id':           self.id,
            'picture':      self.picture,
            'price':        self.price,
            'description':  self.description,
        }

class User(BASE):
    """
    Defines 'User' Table
    """
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    picture = Column(String)
    email = Column(String)
    password_hash = Column(String(64))

    #def hash_password(self, password):
    #    self.password_hash = pwd_context.encrypt(password)

    #def verify_password(self, password):
    #    return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        """
        Creates token to send to client
        """
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    #@staticmethod
    #def verify_auth_token(token):
    #    s = Serializer(secret_key)
    #    try:
    #        data = s.loads(token)
    #    except SignatureExpired:
            # Valid Token, but expired
    #        return None
    #    except BadSignature:
            # Invalid Token
    #        return None
    #    user_id = data['id']
    #    return user_id

ENGINE = create_engine('sqlite:///catalog.db')

BASE.metadata.create_all(ENGINE)
