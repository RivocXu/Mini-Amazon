# Mini-Amazon
# Test guide
## step 1:
git clone https://github.com/RivocXu/Mini-Amazon.git to your virtual machine

## step 2: 
1. go to amazon_server directory
2. open server.py
3. change the following based on your setting:
```
# your world host&port
world_host = 'vcm-xxxxx.vm.duke.edu' 
world_port = 23456
# ups host&port
ups_host = 'vcm-xxxxx.vm.duke.edu'
ups_port = 6666 
```

## step 3:
1. cd fronted and open client.py
2. change the client address based on your setting
```
HOST = 'vcm-xxxxx.vm.duke.edu'
```
## step4:
1. cd amazon_server 
2. run with the following command to initialize the database and add some products
```
python3 database.py
```
3. To add a new product, see if __name__ == '__main__' in database.py
```
# initialize database
dbEngine = create_engine('postgresql://{}:{}@{}:{}/{}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA))
Base.metadata.create_all(dbEngine)
session = sessionmaker(bind=dbEngine)()

# add a product
newproduct1 = Product(description='Product 1', price = 10.0)
session.add(newproduct1)
newproduct2 = Product(description='Product 1', price = 10.0)
session.add(newproduct2)
session.commit()
```
4. After running database.py, the new product should be in your database. You can check it by 'SELECT * from amazon_product;' in psql.

## step5:
1. cd amazon_server 
2. run with the following command to initialize the server
```
python3 server.py
```
## step6:
1. cd fronted 
2. run the following command to run the website
```
python3 manage.py runserver
```
## step7:
once you placed the order from the website, the process will work as expected.

We have already tested this version with Xin's group based on the latest version of gpb.
Feel free to contact us if you have any problems met!

