import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Category, Item, BASE, User


engine = create_engine('sqlite:///catalog.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

user1 = User(
    username='Admin',
    picture ='',
    email='jnacious88@gmail.com',
    )

session.add(user1)
session.commit()

category1 = Category(
    name='football',
    creator=user1
    )

item1 = Item(
    name='Football Cleats',
    description='Cleats for your Feets',
    price='$99.00',
    category=category1,
    creator=user1,
    picture='https://s7d2.scene7.com/is/image/dkscdn/17NIKYYTHLPHMNCSHRBBB_Black_White/',
    date_added=datetime.datetime.now())

item2 = Item(
    name='Receiver Gloves',
    description='Gloves for your hands',
    price='$29.99',
    category=category1,
    creator=user1,
    picture='https://s7d2.scene7.com/is/image/dkscdn/16NIKAVPRKNTGLV2SFTA_Black_White_is/',
    date_added=datetime.datetime.now())

item3 = Item(
    name='Football',
    description='An oblong ball',
    price='$65.00',
    category=category1,
    creator=user1,
    picture='https://upload.wikimedia.org/wikipedia/commons/b/bd/American_Football_1.svg',
    date_added=datetime.datetime.now())

item4 = Item(
    name='Jersey',
    description='Jersey to wear while playing football',
    price='$105.00',
    category=category1,
    creator=user1,
    picture='http://nflshop.frgimages.com/FFImage/thumb.aspx?i=/productImages/_2560000/ff_2560310_full.jpg&w=340',
    date_added=datetime.datetime.now())

item5 = Item(
    name='Airpump',
    description='Pump to inflate football',
    price='$7.99',
    category=category1,
    creator=user1,
    picture='https://images-na.ssl-images-amazon.com/images/I/51CqxT0HmPL._SY355_.jpg',
    date_added=datetime.datetime.now())


# Add first category to database
session.add(category1)
session.commit()
# Add items for first category to database
session.add_all([item1, item2, item3, item4, item5])
session.commit()

category2 = Category(name='tennis', creator=user1)

item1 = Item(
    name='Tennis Racket',
    description='Racket to hit tennis balls with',
    price='$35.99',
    category=category2,
    creator=user1,
    picture='http://media.istockphoto.com/photos/tennis-racket-black-and-white-style-picture-id178479911',
    date_added=datetime.datetime.now())

item2 = Item(
    name='Tennis Balls',
    description='Balls to hit with your tennis racket',
    price='$4.99',
    category=category2,
    creator=user1,
    picture='http://media.istockphoto.com/photos/isolated-yellow-tennis-ball-on-white-picture-id160179174',
    date_added=datetime.datetime.now())

item3 = Item(
    name='Tennis Shoes',
    description='Shoes to play tennis in',
    price='$64.99',
    category=category2,
    creator=user1,
    picture='http://d2s0f1q6r2lxto.cloudfront.net/pub/ProTips/wp-content/uploads/2015/08/WOMENSTENNISSHOES.jpg',
    date_added=datetime.datetime.now())

item4 = Item(
    name='Tennis Shorts',
    description='These go on your legs',
    price='$32.99',
    category=category2,
    creator=user1,
    picture='http://www.csportsfashion.com/wp-content/uploads/2011/03/Nike-N.E.T.-7-Mens-Woven-Tennis-Shorts.jpg',
    date_added=datetime.datetime.now())


item5 = Item(
    name='Tennis Shirt',
    description='This goes on your torso',
    price='$42.99',
    category=category2,
    creator=user1,
    picture='https://slimages.macysassets.com/is/image/MCY/products/8/optimized/3621818_fpx.tif?op_sharpen=1',
    date_added=datetime.datetime.now())


item6 = Item(
    name='Wristbands',
    description='These go on your wrist',
    price='$2.99',
    category=category2,
    creator=user1,
    picture='http://imshopping.rediff.com/imgshop/800-1280/shopping/pixs/17458/n/nike_wrist_band._new-nike-wristbands-tennis-federer-rafa-nadal-sport-wristband.jpg',
    date_added=datetime.datetime.now())

# Add category to database
session.add(category2)
session.commit()
# Add items to database
session.add_all([item1, item2, item3, item4, item5, item6])
session.commit()

category3 = Category(name='basketball', creator=user1)

item1 = Item(
    name='Basketball',
    description='A ball to throw through baskets',
    price='$44.99',
    category=category3,
    creator=user1,
    picture='https://i5.walmartimages.com/asr/62f061c8-9eae-460b-8964-84877f89dfc6_1.63cb4384ad2e3927105b7cfe8aa71fcc.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF',
    date_added=datetime.datetime.now())

item2 = Item(
    name='Basketball Hoop',
    description='A hoop to throw through basketballs through',
    price='$1244.99',
    category=category3,
    creator=user1,
    picture='https://target.scene7.com/is/image/Target/11450049?wid=520&hei=520&fmt=pjpeg',
    date_added=datetime.datetime.now())

item3 = Item(
    name='Basketball Shoes',
    description='Shoes to wear while playing basketball',
    price='$1243.99',
    category=category3,
    creator=user1,
    picture='https://fgl.scene7.com/is/image/FGLSportsLtd/332258243_99_a?wid=288&hei=288&op_sharpen=1&resMode=sharp2',
    date_added=datetime.datetime.now())

item4 = Item(
    name='Basketball Safety Glasses',
    description='Safety First',
    price='$120.00',
    category=category3,
    creator=user1,
    picture='https://alexnld.com/wp-content/uploads/2016/09/cc975270-de2c-4b52-a818-5d9e4a2fb2f3.jpg',
    date_added=datetime.datetime.now())

item5 = Item(
    name='Mouthguard',
    description='To protect them pearly whites',
    price='$12.21',
    category=category3,
    creator=user1,
    picture='https://cdn3.volusion.com/rapgm.jympt/v/vspfiles/photos/UA-1400-A-2.jpg?1478615076',
    date_added=datetime.datetime.now())

# Add category to database
session.add(category3)
session.commit()
# Add items to database
session.add_all([item1, item2, item3, item4, item5])
session.commit()


category4 = Category(name='snowboarding', creator=user1)

item1 = Item(
    name='Snowboard',
    description='A board to ride on the snow',
    price='$644.99',
    category=category4,
    creator=user1,
    picture='https://images.evo.com/imgp/250/121550/526064/never-summer-proto-type-two-snowboard-2018-152.jpg',
    date_added=datetime.datetime.now())

item2 = Item(
    name='Snowboarding Boots',
    description='Boots to wear while snowboarding',
    price='$144.99',
    category=category4,
    creator=user1,
    picture='http://images.the-house.com/32-low-cut-snowboard-boots-black-17-prod.jpg',
    date_added=datetime.datetime.now())

item3 = Item(
    name='Jacket',
    description='You are on a board on the snow... you will need a jacket',
    price='$243.99',
    category=category4,
    creator=user1,
    picture='https://images.evo.com/imgp/250/114303/521925/arc-teryx-iser-jacket-pilot.jpg',
    date_added=datetime.datetime.now())

item4 = Item(
    name='Snowpants',
    description='You think you can just wear your jeans down the snowcovered mountain?',
    price='$120.00',
    category=category4,
    creator=user1,
    picture='http://images.the-house.com/32-blahzay-snowboard-pants-black-17-prod.jpg',
    date_added=datetime.datetime.now())

item5 = Item(
    name='Gloves',
    description='Those fingers gonna get real cold, real quick without gloves.',
    price='$62.21',
    category=category4,
    creator=user1,
    picture='http://scene7.zumiez.com/is/image/zumiez/pdp_hero/Dakine-Omega-Northwoods-Snowboard-Gloves-_264051-front-US.jpg',
    date_added=datetime.datetime.now())

# Add category to database
session.add(category4)
session.commit()
# Add items to database
session.add_all([item1, item2, item3, item4, item5])
session.commit()

category5 = Category(
    name='pingpong',
    creator=user1)

item1 = Item(
    name='Ping Pong Paddle - High Quality',
    description='This is a high quality ping pong paddle',
    price='$14.99',
    category=category5,
    picture='https://www.badmintonbay.com.my/image/data/butterfly/Stayer%201800/butterfly-stayer-1800-00.jpg',
    date_added=datetime.datetime.now())

item2 = Item(
    name='Ping Pong Paddle - Low Quality',
    description='This is a low quality ping pong paddle',
    price='$13.99',
    category=category5,
    picture='https://ae01.alicdn.com/kf/HTB1mdD2PpXXXXawXVXXq6xXFXXXZ/1-Pair-Table-Tennis-Racket-Professional-Ping-font-b-Pong-b-font-font-b-Paddle-b.jpg',
    date_added=datetime.datetime.now())

item3 = Item(
    name='Ping Pong Balls - High Quality',
    description='These are high quality balls to hit with your ping pong paddle',
    price='$5.99',
    category=category5,
    picture='https://www.myactivesg.com/~/media/consumer/images/sports/table%20tennis/gc176_3.jpg',
    date_added=datetime.datetime.now())

item4 = Item(
    name='Ping Pong Balls - Low Quality',
    description='These are low quality balls that you can hit with your ping pong paddle',
    price='$3.99',
    category=category5,
    picture='https://qph.ec.quoracdn.net/main-qimg-de89c3e18b41e106e720d0a8661fb685',
    date_added=datetime.datetime.now())

item5 = Item(
    name='Ping Pong Table',
    description='A table on which to hit the ping pong balls with the ping pong paddles',
    price='$629.42',
    category=category5,
    picture='https://cdn-sportsunlimitedinc.scdn2.secure.raxcdn.com/mod_productImagesDownload/images/tr21table_mainProductImage_FullSize.jpg',
    date_added=datetime.datetime.now())

# Add category to database
session.add(category5)
session.commit()
# Add items to database
session.add_all([item1, item2, item3, item4, item5])
session.commit()

print('items successfully added')
