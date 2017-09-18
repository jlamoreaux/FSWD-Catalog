import os
import sys

from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        '''Returns data in easily serializable format'''
        return {
            'name'  : self.name,
            'id'    : self.id
        }
class Item(Base):
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
        'name'          : self.name,
        'id'            : self.id,
        'picture'       : self.picture,
        'price'         : self.price,
        'description'   : self.description,
        }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
