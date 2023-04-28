import world_amazon_pb2 as world
import amazon_ups_pb2 as au
import communication as c
import amazon_web_pb2 as web
from concurrent.futures import ThreadPoolExecutor
import random
import time
import threading

from database import Product, placeOrder, placeOrderItem, Orders, OrderItem, AmazonUser
from database import init_db

seqnum_list = []
# package_id_list = []
ack_list = []
order_id_list = []  # also used as package id
ups_seqnum_list = []
world_seqnum_list = []
seqnumlock = threading.Lock()
user_id = 1 #initaliztion

# --------------------------------------------------
# 0. general handling techniques
# --------------------------------------------------

# get current sequence number -- tested
def get_cur_seqnum():
    print("start: get_cur_seqnum")
    # seqnumlock.acquire()
    global seqnum_list
    if len(seqnum_list)==0:
        seqnum_list.append(0)
        return 0 
    last_index=max(seqnum_list)
    seqnum_list.append(last_index+1)    # add new seqnum to the list
    print("cur seq num is",last_index)
    # seqnumlock.release()
    return last_index+1
    # global seqnum
    # seqnum = seqnum + 1
    # temp_num = seqnum
    # return temp_num

# get current package id -- tested
def get_cur_packid():
    tmp = order_id_list[0]
    order_id_list.pop(0)
    return tmp  # get the first element of the queue

# if current sequence number is in the ack_world list -- useless
def check_ifack(cur_seqnum):
    if cur_seqnum in ack_list:
        return True
    else: return False

# add all ack to the ack list  # -- tested
def handle_ack(acks):   
    print("handle ack")
    print("ack list is:")
    global acks_list
    print(ack_list)
    for ack in acks:
        ack_list.append(ack)
    return


# send ack to the world
def send_ack_world(socket,seqnum):
    # global world_seqnum_list
    ack_sent = world.ACommands()
    ack_sent.acks.append(seqnum)
    c.send_message_to(socket,ack_sent)
    if seqnum not in world_seqnum_list:
        world_seqnum_list.append(seqnum)
        print("world_seqnum_list is",world_seqnum_list)
    return

# send ack to ups
def send_ack_ups(socket,seqnum):
    # print(seqnum)
    # global ups_seqnum_list
    ack_sent = au.AmazonCommands()
    ack_sent.acks.append(seqnum)
    c.send_message_to(socket,ack_sent)
    if seqnum not in ups_seqnum_list:
        ups_seqnum_list.append(seqnum)
        print("ups_seqnum_list is",ups_seqnum_list)
    return

def transfer_item(message_initship,arrived):
    pass

# send the message repetitively until receive ack
def send_till_ack(socket,command,cur_seqnum):
    while 1:
        print("command sent is:")
        print(command)
        c.send_message_to(socket,command)
        time.sleep(5)  # sleep 10 seconds to wait for ack before retransmission
        if cur_seqnum in ack_list:
            print("message {} has been acknowledged".format(cur_seqnum))
            break
        print(ack_list)
    return

# --------------------------------------------------
# 1. handle request from the world
# --------------------------------------------------

# handle purchase more
def handle_purchasemore(amazon_ups_socket,amazon_world_socket,arrived):
    # # avoid duplicate
    # if arrived.seqnum in world_seqnum_list:
    #     return

    # a. send ack to world
    print("handle arrived")
    print(arrived)
    send_ack_world(amazon_world_socket,arrived.seqnum)

    # b. prepare message sent to ups
    command_sent = au.AmazonCommands()
    #command details
    message_initship=au.AmazonUPSInitShip()
    message_initship.id = get_cur_seqnum()  # based on the cur_seqnm list
    message_initship.wid = arrived.whnum

    # transfer item from world to the ups
    for thing in arrived.things:
        product = au.Item()
        product.description = thing.description
        product.quantity = thing.count
        message_initship.items.append(product)
    # package id should be initialized here
    message_initship.packageid = get_cur_packid()   # based on the current package id list-->只有在purchasemore处才需要有新的package id

    # --------------------------------------------------
    # --------------------database-2---------------------
    # --------------------------------------------------  
    # --to do: 把whnum写入
    # --to do: 根据packageid去数据库里调destination address--
    # get from the database
    # message_initship.x = order.addr_x   # dest address of order
    # message_initship.x = 12
    # # message_initship.y = order.addr_y
    # message_initship.y = 12
    # # ------------------TODO: fetch from db-------------------
    order_id = message_initship.packageid
    dbSession = init_db()
    order = dbSession.query(Orders).filter_by(id = order_id).first()
    user = dbSession.query(AmazonUser).filter_by(user_name = order.user_name).first()
    message_initship.userID = user.id
    # --------------------------------------------------

        # --------------------database-2---------------------
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    wh_id = 1
    wh_location_x = 12
    wh_location_y = 12
    Order.wh_id = wh_id
    Order.wh_location_x = wh_location_x
    Order.wh_location_y = wh_location_y
    dbSession.commit()
    
    # --------------------------------------------------- 
    
    
    # message_initship.x = order.addr_x   # dest address of order
    # message_initship.x = 12
    # message_initship.y = order.addr_y
    # message_initship.y = 12
    message_initship.x = Order.location_x
    message_initship.y = Order.location_y
    # --------------------------------------------------



    command_sent.initship.append(message_initship)
    print(command_sent)

    # c.send_message_to(amazon_ups_socket,message_initship)
    send_till_ack(amazon_ups_socket,command_sent,message_initship.id)
    print("---already send initship to ups")
    # dbSession.close()
    return


# handle packed
def handle_packed(amazon_world_socket,amazon_ups_socket,packed):
    # # avoid duplicate
    # if packed.seqnum in world_seqnum_list:
    #     return

    print("handle packed")
    # a. send ack to world
    send_ack_world(amazon_world_socket,packed.seqnum)

    # b. send message to ups
    command_sent = au.AmazonCommands()
    message_startship=au.AmazonUPSStartShip()
    message_startship.id = get_cur_seqnum()
    message_startship.packageid = packed.shipid
    command_sent.startship.append(message_startship)
    # c.send_message_to(amazon_ups_socket,message_initship)
    # print("startship start")

    order_id = packed.shipid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = 'packed'
    dbSession.commit()

    print(command_sent)
    send_till_ack(amazon_ups_socket,command_sent,message_startship.id)
    print("---already send startship to ups")
    # dbSession.close()
    return

# handle loaded
def handle_loaded(amazon_world_socket,amazon_ups_socket,loaded):
    print("handle loaded")
    # a. send ack to world
    send_ack_world(amazon_world_socket,loaded.seqnum)
    # b. fill the message
    command_sent = au.AmazonCommands()
    message_finishship = au.AmazonUPSFinishShip()
    message_finishship.id = get_cur_seqnum()
    message_finishship.packageid = loaded.shipid
    command_sent.finishship.append(message_finishship)
    # c. change status to loaded
    order_id = message_finishship.packageid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = 'loaded'
    dbSession.commit()
    # dbSession.close()
    # d.send_message_to(amazon_ups_socket,message_finishship)
    send_till_ack(amazon_ups_socket,command_sent,message_finishship.id)
    # e. change status to delivering
    order_id = loaded.shipid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = 'delivering'
    dbSession.commit()
    # dbSession.close()
    return

# handle package status
def handle_packagestatus(amazon_world_socket,packagestatus):
    print("handle packagestatus")
    # a. 发送ack
    send_ack_world(amazon_world_socket,packagestatus.seqnum)
    # b. load status
    order_id = packagestatus.packageid
    status = packagestatus.status
    status = status.lower()

    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = status
    dbSession.commit()
    # dbSession.close()

    return

# handle finish command
def handle_finished():
    pass

def handle_error():
    pass

# --------------------------------------------------
# 2. handle request from UPS
# --------------------------------------------------

def handle_UAInit(amazon_ups_socket,amazon_world_socket,initship):
    #     # avoid duplicate
    # if initship.id in ups_seqnum_list:
    #     return
    print("handle UAInit")
    # print(initship)
    # a. send an ack back to ups five times
    send_ack_ups(amazon_ups_socket,initship.id)

    # --------------------------------------------------
    # --------------------database-3---------------------
    # --------------------------------------------------  
    # ------------to do: 把truck id 写入数据库------------
    # --------------------database-3---------------------
    order_id = initship.packageid
    dbSession = init_db()
    myOrder = dbSession.query(Orders).filter_by(id = order_id).first()
    tid = initship.truckid

    # myOrder.update(truck_id = tid)
    myOrder.truck_id = tid
    # myOrder.save()
    dbSession.commit()

    # c. send message to world
    # initialize the message
    command_sent = world.ACommands()
    message_pack = world.APack()

    # --------------------------------------------------
    # --------------------database-4---------------------
    # --------------------------------------------------  
    # ----to do: 根据package id从数据库中读取whid，items---

    # --------------------database-4---------------------
    order_id = initship.packageid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    wh_id = Order.wh_id
    items = Order.order_items
    # dbSession.commit()
    # ---------------------------------------------------
    # message_pack.whnum = get_whnum(db,initship.packageid)
    message_pack.whnum = wh_id # used for testing
    # message_pack.things = get_items(db,initship.packageid)  #get item from the database based on pid
    for item in items:
        tmp_product = world.AProduct()  # used for testing
        # tmp_product.id = item.product.id
        # tmp_product.description = "description"
        # tmp_product.count = 10
        tmp_product.id = item.product.id
        print(item.product.id)
        tmp_product.description = item.product.description
        tmp_product.count = item.count
        message_pack.things.append(tmp_product)
        # print(item.product.id)
    message_pack.shipid = initship.packageid
    message_pack.seqnum = get_cur_seqnum()
    command_sent.topack.append(message_pack)
    print("current seq num is",message_pack.seqnum)
    # send out the message
    # d.send_message_to(amazon_world_socket,message_pack)
    print(command_sent)
    send_till_ack(amazon_world_socket,command_sent,message_pack.seqnum)
    print("---already sent pack to world & handled UAinit")
    # dbSession.close()
    return


# def handle_UAStart(amazon_ups_socket,amazon_world_socket,startship,db):
def handle_UAStart(amazon_ups_socket,amazon_world_socket,startship):
    # if startship.id in ups_seqnum_list:
    #     return
    # a. send an ack back to ups
    send_ack_ups(amazon_ups_socket,startship.id)
    # b. fill the message
    command_sent = world.ACommands()
    message_load = world.APutOnTruck()
    message_load.whnum = 1
    # message_load.whnum = get_whnum(db,startship.packageid)  # to do from database
    # message_load.truckid = startship.truckid    # ----------------TODO: read from db-----------------
    order_id = startship.packageid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    truck_id = Order.truck_id

    message_load.truckid = truck_id
    message_load.shipid = startship.packageid
    message_load.seqnum = get_cur_seqnum()
    command_sent.load.append(message_load)
    # c.send_message_to(amazon_world_socket,message_load)
    
    # change status
    order_id = startship.packageid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = 'loading'
    dbSession.commit()
    # dbSession.close()
    send_till_ack(amazon_world_socket,command_sent,message_load.seqnum)
    # dbSession.close()
    return


def handle_UAFin(amazon_ups_socket,finship):
    # a. send an ack back to ups
    send_ack_ups(amazon_ups_socket,finship.id)
    # -----------TODO: change db message-------------
    order_id = finship.packageid
    dbSession = init_db()
    Order = dbSession.query(Orders).filter_by(id = order_id).first()
    Order.status = 'delivered'
    dbSession.commit()
    # dbSession.close()
    return


def get_random_whnum():
    rand_whlist=[1] # to do: current: 1 
    random_index = random.randint(1, len(rand_whlist)+1)
    return 1

# --------------------------------------------------
# 3. handling web part 
# --------------------------------------------------
def handle_buy(amazon_world_socket,products): 
    print("Handle buy")
    # encapsulate information in the command
    command=world.ACommands()
    command_buy=world.APurchaseMore()
    command_buy.whnum=get_random_whnum()
    # for product in order.products: 一次只发一个product
    for product in products:
        command_buy.things.append(product)
    command_buy.seqnum=get_cur_seqnum()
    command.buy.append(command_buy)
    # print(command)
    
    send_till_ack(amazon_world_socket,command,command_buy.seqnum)
    print("--already sent query more to amazon!")
    return

def handle_Query(amazon_world_socket,order_id):
    # send query to world till ack
    command = world.ACommands()
    command_query = world.AQuery()
    command_query.packageid = order_id
    command_query.seqnum = get_cur_seqnum()
    command.queries.append(command_query)
    send_till_ack(amazon_world_socket,command,command_query.seqnum)
    print("--already sent query status to amazon!")

# close connection with the server
def finish_connection(socket):
    command=world.ACommands()
    command.disconnect=True
    c.send_message_to(socket,command)
    return
    
# --------------------------------------------------
# 4. overall handling part 
# --------------------------------------------------
# handle request from web
# def handle_web_amazon(amazon_world_socket):   #TODO:test
def handle_web_amazon(amazon_web_socket,amazon_world_socket):
    while True:   # test

        print("---------------Handle web-amazon---thread1------------")
        # for every order id received, add to the list
        # keep listening from web
        received_message = c.keep_listen_to_web(amazon_web_socket)
        # ------handle query
        if 'check status' in received_message:
            order_id = int(received_message.split(': ')[1])
            handle_Query(amazon_world_socket,order_id)
            return
        # ------handle buy
        else:
            order_id=int(received_message)

        # order_id = 1    #TEST
        print(order_id)
        print(type(order_id))

        #-----------------------------------------------------------
        #----------------------------Database-1----------------------
        #-----------------------------------------------------------
        # ----------------------------to do-------------------------
        # 1. 根据orderid去调用前端数据库里的相关信息
        # 2. 将调用的东西存到新的table里()
        # 3. 再根据新的order id去调用相应的信息

        #----------------------------Database-1----------------------
        dbSession = init_db()
        placedOrder = dbSession.query(placeOrder).filter_by(id = order_id).first()
        newOrder = Orders(user_name=placedOrder.user_name, location_x=placedOrder.location_x, location_y=placedOrder.location_y, status='packing')
        for item in placedOrder.items:
            newItem = OrderItem(order_id=newOrder.id, product_id=item.product_id, count=item.count)
            newOrder.order_items.append(newItem)
        dbSession.add(newOrder)
        user = dbSession.query(AmazonUser).filter_by(user_name = newOrder.user_name).first()
        if not user:
            newUser = AmazonUser(user_name=newOrder.user_name)
            dbSession.add(newUser)
        dbSession.commit()
        #-----------------------------------------------------------
        
        global order_id_list
        order_id = newOrder.id
        order_id_list.append(order_id)
        print("order id list is:")
        print(order_id_list)

        response = web.order()
        # -------------can fetch from db: product information-------

        for item in newOrder.order_items:
            print("item is")
            print(item.product.description)
            tmp_product = world.AProduct()
            tmp_product.id = item.product.id
            tmp_product.description = item.product.description
            tmp_product.count = item.count
            response.products.append(tmp_product)
            print(tmp_product)
        # -------------can fetch from db: product information-------


        # print(response)
        # for i in range(len(response.order)):
        # if response.HasField("products"):
        
        handle_buy(amazon_world_socket,response.products)    #一次只发一个product
        # dbSession.close()
    # return  # test
        

# handle the request between world and amazon
def handle_world_amazon(amazon_world_socket,amazon_ups_socket):
    print("handle world amazon---thread3")
    # initialize the thread
    thread_count=10 # defaul value: 10
    executor = ThreadPoolExecutor(max_workers=thread_count)

    # keep listening from amazon and world
    while True:

        # receive message from world
        response = c.receive_message_from(amazon_world_socket,world.AResponses)
        print("------------receive message from the world------------")
        print(response)
        # parse the response
        # for ack in response.acks:
        if len(response.acks)!=0:
            # threadpool.submit(handle_ack,response.acks)    #一次只发一个product
            print("check ack world")
            # handle_ack(response.acks)
            executor.submit(handle_ack,response.acks)    #一次只发一个product
        for i in range(len(response.arrived)):
        # if len(response.arrived)!=0:
                # avoid duplicate
            if response.arrived[i].seqnum in world_seqnum_list:
                continue
            print("check arrived")
            print(response.arrived[i])
            executor.submit(handle_purchasemore,amazon_ups_socket,amazon_world_socket,response.arrived[i])
            # handle_purchasemore(amazon_ups_socket,amazon_world_socket,response.arrived[i])
            # handle_purchasemore(amazon_ups_socket,amazon_world_socket,response.arrived)
        for i in range(len(response.ready)):
                            # avoid duplicate
            print("check packed or not")
            print(response.ready[i])
            if response.ready[i].seqnum in world_seqnum_list:
                continue
            executor.submit(handle_packed,amazon_world_socket,amazon_ups_socket,response.ready[i])
        for i in range(len(response.loaded)):
            if response.loaded[i].seqnum in world_seqnum_list:
                continue
            print("check loaded or not")
            print(response.loaded[i])
            executor.submit(handle_loaded,amazon_world_socket,amazon_ups_socket,response.loaded[i])
        # if response.finished!=0:
        #     handle_finished()
        for i in range(len(response.error)):
            print("handle error")
            print(response.error[i])
            executor.submit(handle_error,amazon_world_socket,amazon_ups_socket,response.error[i])
        for i in range(len(response.packagestatus)):
            if response.packagestatus[i].seqnum in world_seqnum_list:
                continue
            print("check package status")
            print(response.packagestatus)
            executor.submit(handle_packagestatus,amazon_world_socket,response.packagestatus[i])
    # threadpool.shutdown(wait=True)
    return

# handle the request between amazon and ups
def handle_amazon_ups(amazon_ups_socket,amazon_world_socket):
    print("handle amazon ups---thread2")
    # initialize the thread
    thread_count=10 # defaul value: 10
    executor = ThreadPoolExecutor(max_workers=thread_count)

    while True:
        response = c.receive_message_from(amazon_ups_socket,au.UPSCommands)
        print("------------receive message from the ups----------")
        print(response)
        # parse the response
        # for ack in repeated acks
        if len(response.acks)!=0:
            print("check ups ack")
            executor.submit(handle_ack,response.acks)    #一次只发一个product
            # handle_ack(response.acks)
        for i in range(len(response.initship)):
            # if len(response.arrived)!=0:
            if response.initship[i].id in ups_seqnum_list:
                continue
            print("check initship")
            print(response.initship[i])
            executor.submit(handle_UAInit,amazon_ups_socket,amazon_world_socket,response.initship[i])
            # handle_UAInit(amazon_ups_socket,amazon_world_socket,response.initship[i],1)
            # handle_purchasemore(amazon_ups_socket,amazon_world_socket,response.arrived)
        for i in range(len(response.startship)):
            if response.startship[i].id in ups_seqnum_list:
                continue
            print("check startship")
            print(response.startship[i])
            executor.submit(handle_UAStart,amazon_ups_socket,amazon_world_socket,response.startship[i])
        for i in range(len(response.finishship)):
            if response.finishship[i].id in ups_seqnum_list:
                continue
            print("check finishship")
            print(response.finishship[i])
            executor.submit(handle_UAFin,amazon_ups_socket,response.finishship[i])
        for i in range(len(response.error)):
            handle_error()





