from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Category, Item, BASE
import datetime

engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

category1 = Category(name='football')

item1 = Item(name='Football Cleats', description='Cleats for your Feets', price='$99.00', category=category1, picture='https://s7d2.scene7.com/is/image/dkscdn/17NIKYYTHLPHMNCSHRBBB_Black_White/', date_added=datetime.datetime.now())

item2 = Item(name='Receiver Gloves', description='Gloves for your hands', price='$29.99', category=category1, picture='https://s7d2.scene7.com/is/image/dkscdn/16NIKAVPRKNTGLV2SFTA_Black_White_is/', date_added=datetime.datetime.now())

session.add(category1)
session.commit()
session.add_all([item1, item2])
session.commit()

category2 = Category(name='tennis')

item1 = Item(name='Tennis Racket', description='Racket to hit tennis balls with', price='$35.99', category=category2, picture='http://media.istockphoto.com/photos/tennis-racket-black-and-white-style-picture-id178479911', date_added=datetime.datetime.now())

item2 = Item(name='Tennis Balls', description='Balls to hit with your tennis racket', price='$4.99', category=category2, picture='http://media.istockphoto.com/photos/isolated-yellow-tennis-ball-on-white-picture-id160179174', date_added=datetime.datetime.now())

session.add(category2)
session.commit()
session.add_all([item1, item2])
session.commit()


print('test items added')
