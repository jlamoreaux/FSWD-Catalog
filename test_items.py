from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Category, Item, BASE

engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name='football')

item1 = Item(name='Football Cleats', description='Cleats for your Feets', price='$99.00', category=category1)

item2 = Item(name='Receiver Gloves', description='Gloves for your hands', price='$29.99', category=category1)

category2 = Category(name='tennis')

item3 = Item(name='Tennis Racket', description='Racket to hit tennis balls with', price='$35.99', category=category2)

item4 = Item(name='Tennis Balls', description='Balls to hit with your tennis racket', price='$4.99', category=category2)

session.add_all([category1, category2])
session.commit()

session.add_all([item1, item2, item3, item4])
session.commit()

print('test items added')
