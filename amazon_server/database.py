from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
# from flask_login import UserMixin
from sqlalchemy import Column, String, Integer, Text, ForeignKey, Float
from sqlalchemy.types import Enum
import enum
from sqlalchemy import text

# Config
DB_USER = 'postgres'                # Username
DB_PASSWORD = 'abc123'            # Password
#DB_HOST = 'vcm-33567.vm.duke.edu'   # Host name
DB_HOST = 'localhost'
DB_PORT = '5432'                    # Port number
DB_SCHEMA = 'project'              # Database name


Base = declarative_base()

class Product(Base):
    __tablename__ = 'amazon_product'
    id = Column(Integer, primary_key=True)
    description = Column(String(64))
    price = Column(Float(precision=2))

class placeOrder(Base):
    __tablename__ = 'amazon_placeorder'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(64))
    location_x = Column(Integer)
    location_y = Column(Integer)
    items = relationship('placeOrderItem', back_populates='order', cascade='all, delete-orphan', lazy='joined')

class placeOrderItem(Base):
    __tablename__ = 'amazon_placeorderitem'
    order_id = Column(Integer, ForeignKey('amazon_placeorder.id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('amazon_product.id'), primary_key=True)
    count = Column(Integer, default=0)
    products = relationship('Product', back_populates='placeorders')
    order = relationship('placeOrder', back_populates='items')
Product.placeorders = relationship('placeOrderItem', back_populates='products')



# class Warehouse(Base):
#     __tablename__ = "amazon_warehouse"
    
#     id = Column(Integer, primary_key = True)
#     location_x = Column(Integer)
#     location_y = Column(Integer)
    
#     def __init__(self, x, y):
#         self.location_x = x
#         self.location_y = y
        
# class orderStatus(enum.Enum):
#     zero = 'cart'
#     one = 'packing'
#     two = 'packed'
#     three = 'loading'
#     four = 'loaded'
#     five = 'delivering'
#     six = 'delivered'

class Orders(Base):
    __tablename__ = "amazon_orders"
    
    id = Column(Integer, primary_key = True)
    user_name = Column(String(64))
    location_x = Column(Integer)            # destination x
    location_y = Column(Integer)            # destination y
    wh_id = Column(Integer, nullable = True)
    wh_location_x = Column(Integer, nullable = True)            # destination x
    wh_location_y = Column(Integer, nullable = True)            # destination y
    truck_id = Column(Integer, nullable = True)
    status = Column(Enum('cart', 'packing', 'packed', 'loading', 'loaded', 'delivering', 'delivered', name='order_status'))
    note = Column(Text, nullable = True)
    order_items = relationship('OrderItem', back_populates='order')
    
    def __init__(self, user_name, location_x, location_y, status, wh_id = None, wh_location_x=None, wh_location_y=None, truck_id = None, note = None):
        self.user_name = user_name
        self.location_x = location_x
        self.location_y = location_y
        self.wh_id = wh_id
        self.wh_location_x = wh_location_x
        self.wh_location_y = wh_location_y
        self.truck_id = truck_id
        self.status = status
        self.note = note

class OrderItem(Base):
    __tablename__ = 'amazon_orderitem'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('amazon_orders.id'))
    product_id = Column(Integer, ForeignKey('amazon_product.id'))
    count = Column(Integer)
    product = relationship('Product', back_populates='orders')
    order = relationship('Orders', back_populates='order_items')
    
    def __init__(self, order_id, product_id, count):
        self.order_id = order_id
        self.product_id = product_id
        self.count = count

Product.orders = relationship('OrderItem', back_populates='product')

class AmazonUser(Base):
    __tablename__ = 'amazonuser'
    id = Column(Integer, primary_key=True)
    user_name = Column(String(64))

    def __init__(self, user_name):
        self.user_name = user_name

        
# Initialize database
def init_db():
    # Initialize connection
    dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA))
    Base.metadata.create_all(dbEngine)
    # Create a new session object (Call __call__() method by ())
    dbSession = sessionmaker(bind=dbEngine)()
    return dbSession


def drop_tables():
    dbSession = init_db()
    dbSession.execute(text('DROP TABLE IF EXISTS USERS, WAREHOUSES, ITEMS, ORDERS, PACKAGES, PlaceOrder CASCADE'))
    dbSession.execute(text('DROP TYPE IF EXISTS ORDERSTATUS'))
    dbSession.commit()
    #dbSession.close()

# ==================================== TEST ====================================     
# def add_testing_data():
#     dbSession = init_db()
    
#     User1 = Users(name = 'Taylor Swift', email = 'ts@gmail.com', password = '12345', x = 22, y = 22, ups_name = 'UPS')
#     User2 = Users(name = 'Ed Sheeran', email = 'es@gmail.com', password = '12345', x = 22, y = 22, ups_name = 'UPS')
    
#     WH1 = Warehouses(x = 10, y = 10)
#     WH2 = Warehouses(x = 9, y = 9)
    
#     Item1 = Items(d = 'PS5')
#     Item2 = Items(d = 'Macbook')
    
#     dbSession.add(User1)
#     dbSession.add(User2)
    
#     dbSession.add(WH1)
#     dbSession.add(WH2)
    
#     dbSession.add(Item1)
#     dbSession.add(Item2)
    
#     # Stock1 = Stocks(item_id = Item1.id, count = 1, wh_id = WH1.id)
#     # Stock2 = Stocks(item_id = Item1.id, count = 0, wh_id = WH2.id)
#     # Stock3 = Stocks(item_id = Item2.id, count = 0, wh_id = WH1.id)
#     # Stock4 = Stocks(item_id = Item2.id, count = 1, wh_id = WH2.id)
    
#     # dbSession.add(Stock1)
#     # dbSession.add(Stock2)
#     # dbSession.add(Stock3)
#     # dbSession.add(Stock4)
    
#     dbSession.commit()
#     #dbSession.close()

# def test():
#     print("Test")
#     drop_tables()
#     dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA))
    
#     Base.metadata.create_all(dbEngine)
#     print("Tables created")
#     #add_testing_data()
#     print("Data added")
    
if __name__ == '__main__':
    # test()
    # drop_tables()
    print("Test placeOrder")
    dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA))
    Base.metadata.create_all(dbEngine)
    session = sessionmaker(bind=dbEngine)()
    # records = session.query(placeOrder).all()
    # print("Query result:")
    # for record in records:
    #     print(f"ID: {record.id}")
    #     print(f"User name: {record.user_name}")
    #     print(f"Location x: {record.location_x}")
    #     print(f"Location y: {record.location_y}")
    #     print(f"Item ID: {record.item_id}")
    #     print(f"Count: {record.count}")
    #     print(f"Description: {record.description}")
    records = session.query(placeOrderItem).all()
    print("Query result:")
    for record in records:
        print(f"Order id: {record.order_id}")
        print(f"Product id: {record.product_id}")
        print(f"Count: {record.count}")
        print(f"Product id2: {record.products.id}")
        print(f"Description: {record.products.description}")
    print()
    # aorder = Orders(user_name="user1", location_x=10, location_y=10, status=orderStatus.one)
    # newproduct = Product(description='Product 2', price = 20.0)
    # session.add(newproduct)
    # # aorder = Orders(user_name='user1', location_x=10, location_y=10, wh_id=1,
    # #                wh_location_x=246, wh_location_y=369, truck_id=1,
    # #                status='packing', note='Test order')
    # # session.add(aorder)
    # # new_order_item = OrderItem(order_id=1, product_id=1, count=3)
    # # session.add(new_order_item)
    # session.commit()
    # print(orderStatus.zero)
    
    print("Retrieve Data")
    records = session.query(Orders).all()
    for record in records:
        print(f"User name: {record.user_name}")
        print(f"Location x: {record.location_x}")
        print(f"Location y: {record.location_y}")
        print(f"Status: {record.status}")
        for item in record.order_items:
            print(f"Description: {item.product.description}")
            print(f"Count: {item.count}")
        print("OK")
        
    # placedOrder = session.query(placeOrder).filter_by(id = 1).first()
    # newOrder = Orders(user_name=placedOrder.user_name, location_x=placedOrder.location_x, location_y=placedOrder.location_y, status='packing')
    # for item in placedOrder.items:
    #     newItem = OrderItem(order_id=newOrder.id, product_id=item.product_id, count=item.count)
    #     newOrder.order_items.append(newItem)
    # session.add(newOrder)
    # session.commit()
    print("Success")