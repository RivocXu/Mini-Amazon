import communication as c
import command_handler as ch
import threading
import time
import socket

world_host = 'vcm-32866.vm.duke.edu'
# world_host = 'vcm-30735.vm.duke.edu'
world_port = 23456
ups_host = 'vcm-32866.vm.duke.edu'
ups_port = 6666 
web_host = socket.gethostname()
web_port = 8888  # 监听的端口



# main handling part
def main():
    ## --------initialization--------
    # connect to world server
    amazon_world_socket=c.connect_to_world_server(world_host,world_port) 

    # connect to ups serverxw
    amazon_ups_socket=c.connect_to_ups_server(ups_host,ups_port)

    # connect to database
    amazon_web_socket = c.connect_to_web(web_host,web_port)

    # send back message if successfully connected
    world_id=c.amazon_ups_init(amazon_ups_socket)
    print(world_id)

    # world_id = 1
    aw_success_indicator=c.amazon_world_init(amazon_world_socket,world_id)
    # if not successfully connected
    if not aw_success_indicator:
        print("Connection between world and amazon failed\n")
        return 0  
    if aw_success_indicator:
        print("Successful Connection between world and amazon\n")
        
    ## ---------command handling part-----------
    # 三个thread，一直监听
    # 一个thread和前端
    # 一个thread和amazon
    # 一个thread和ups
    ###------test！！！！！！！！！！！---------####
    # tmp_product = c.world.AProduct()
    # tmp_product.id = 1
    # tmp_product.description = "description"
    # tmp_product.count = 10
    # command_sent = c.world.ACommands()
    # command=c.world.ACommands()
    # command_buy=c.world.APurchaseMore()
    # command_buy.whnum=1
    # # for product in order.products: 一次只发一个product
    # command_buy.things.append(tmp_product)
    # command_buy.seqnum=1
    # command.buy.append(command_buy)

    # c.send_message_to(amazon_world_socket,command)

    # command_sent = c.world.ACommands()
    # message_pack = c.world.APack() 
    # # 根据package id从数据库中读取whid，items
    # # message_pack.whnum = get_whnum(db,initship.packageid)
    # message_pack.whnum = 1 # used for testing
    # # message_pack.things = get_items(db,initship.packageid)  #get item from the database based on pid
    # tmp_product = c.world.AProduct()
    # tmp_product.id = 1
    # tmp_product.description = "description"
    # tmp_product.count = 10
    # message_pack.things.append(tmp_product)
    # message_pack.shipid = 1
    # message_pack.seqnum = 2
    # command_sent.topack.append(message_pack)

    # c.send_message_to(amazon_world_socket,command_sent)
    thread_web = threading.Thread(target = ch.handle_web_amazon, args = (amazon_web_socket,amazon_world_socket))
    # thread_web = threading.Thread(target = ch.handle_web_amazon, args = (amazon_world_socket,))

    thread_UPS = threading.Thread(target=ch.handle_amazon_ups,args=(amazon_ups_socket,amazon_world_socket))
    # amazon_ups_socket = 1
    thread_world = threading.Thread(target=ch.handle_world_amazon,args=(amazon_world_socket,amazon_ups_socket))
    
    # # thread_UPS.start()
    thread_web.start()
    thread_world.start()
    thread_UPS.start()
    
    # # # thread completion
    # # thread_UPS.join()
    # thread_world.join()
    # thread_web.join()
    
    # ch.handle_web_amazon(amazon_world_socket)
    # time.sleep(10)
    # ch.handle_world_amazon(amazon_world_socket,amazon_ups_socket)

if __name__=="__main__":
    main()