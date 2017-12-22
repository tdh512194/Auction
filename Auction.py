import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, Column, Integer, String, ForeignKey, DateTime, Float


app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    start_time = Column(DateTime)
    price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=False) # AUCTION rlts

    bid_item_id = db.relationship('Bid', backref='item', lazy=True) #BID rlts

    def __init__(self, id, name, description, start_time, price, owner_id):
        self.id = id
        self.name = name
        self.description = description
        self.start_time = start_time
        self.price = price
        self.owner_id = owner_id
        print("Create item ", name,
              " ID: ", id)

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

    auction_item = db.relationship('Item', backref='user', lazy=True) # AUCTION rlts
    bid_user_id = db.relationship('Bid', backref='user', lazy=True) # BID rlts

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        print("Create user ", username,
              " ID: ", id)

    def auction(self, item_id, item_name, item_des, item_time, price ):
        "Auction action"
        item = Item.query.filter_by(id = item_id).first()
        if item is None: # check item existence
            item = Item(item_id, item_name, item_des, item_time, price, self.id) # create item in DB
            db.session.add(item)
            db.session.commit()
            print("User ", self.username,
              " place item ", item_name,
              " on auction for ", price)
        else:
            print("Item has existed.")



    def bid(self, item_id, price):
        "Bid action"
        bid = Bid.query.filter_by(item_id = item_id).filter_by(user_id = self.id).first() #select the corresponding row entry, select composite Pkey with 'and_'
        aucprice = Item.query.get(item_id).price
        if price >= aucprice: # bid price must be higher than auction price
            if bid is None: # user has NOT bidded on the item
                bid = Bid(self.id, item_id, price) # create bid session in DB
                db.session.add(bid)
                print("User ", self.username,
                      " successfully bids ", price,
                      " on the ", Item.query.filter_by(id = item_id).first().name)
            else: # user has bidded on the item
                bid.price = price # update the existing price
                print("User ", self.username,
                      " sucessfully bids again ", price,
                      " on the ", Item.query.filter_by(id = item_id).first().name)
            db.session.commit()
        else:
            print(self.username,
                  "must bid higher than ", aucprice,
                  "for the ", Item.query.get(item_id).name)

class Bid(db.Model):
    __tablename__ = 'bid'
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    item_id = Column(Integer, ForeignKey('item.id'), primary_key=True)
    price = Column(Float, nullable=False)

    def __init__(self, user_id, item_id, price):
        self.user_id = user_id
        self.item_id = item_id
        self.price = price

u1 = User(1, 'USERNAME1', 'PASS1')
u2 = User(2, 'USERNAME2', 'PASS2')
u3 = User(6, 'USERNAME6', 'PASS6')

@app.route('/')
def hello_world():

    db.create_all()

    add_user()

    user_auction()

    user_bid()

    query(1)
    query(10)
    query(3)
    return 'Hello World!'

def add_user():
    db.session.add(u1)
    db.session.add(u2)
    db.session.add(u3)

    db.session.commit()

def user_auction():
    u1.auction(1, 'baseball', 'an ordinary baseball', datetime.datetime.utcnow(), 300)
    u2.auction(10, 'teeth', 'his whole teeth', datetime.datetime.utcnow(), 2000)
    u1.auction(3, 'LCD', '40 inch LCD', datetime.datetime.utcnow(), 5000)

def user_bid():
    u2.bid(1, 400)
    u3.bid(1, 200)
    u3.bid(1, 1000)

    u1.bid(10, 2100)
    u3.bid(10, 3000)
    u1.bid(10, 2500)

    u2.bid(3, 5500)
    u3.bid(3, 5600)
    u2.bid(3, 7000)

def query(item_id):
    query_result = Bid.query.filter_by(item_id = item_id).all()
    max = 0;
    for bid in query_result:
        if bid.price >= max:
            max = bid.price
            name = User.query.get(bid.user_id).username # get by primary key

    print(name, " has the highest bid of ", max)

if __name__ == '__main__':
    app.run(debug = True)


