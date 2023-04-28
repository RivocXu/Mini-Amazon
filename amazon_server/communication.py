# establish communication with world & ups

import socket
import world_amazon_pb2 as world
import world_ups_pb2 as world2
import amazon_ups_pb2 as au
import sys
from google.protobuf.internal.encoder import _EncodeVarint
from google.protobuf.internal.decoder import _DecodeVarint32

## used to connect to the world server
def connect_to_world_server(host,port):
    print("connect to world server")
    # create a socket object
    amazon_world_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # establish connection with server
    try:
        amazon_world_socket.connect((host,port))
    except ConnectionRefusedError:
        print("Failed to connect to the world server\n")
    # Handle the failed connection appropriately
    # else:
    #     print("Successfully connected to the world server\n")
    # Perform communication with the server here
    return amazon_world_socket

## used to connect to the ups server
def connect_to_ups_server(host,port):
    print("connect to ups server\n")
    # create a socket object
    amazon_ups_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # establish connection with ups server
    try:
        amazon_ups_socket.connect((host,port))
    except ConnectionRefusedError:
        print("Failed to connect to the ups server\n")
    # Handle the failed connection
    else:
        print("Successfully connected to the ups server\n")
    # Perform communication with the ups server here
    return amazon_ups_socket

## wrap up: send certain message to certain socket 
def send_message_to(socket,message):
    print("send message to server")
    print("message sent is: ")
    print(message)
    # convert gpf to transmittable binary string
    serialized_message = message.SerializeToString()


    # encode the message sent
    _EncodeVarint(socket.send,len(serialized_message),None)

    # send the message
    bytes_sent=socket.send(serialized_message)

    # check if sent successfully
    if bytes_sent==0:
        print("Sending failure")
        return False

## wrap up: receive gpb object from certain socket
def receive_message_from(socket,messagetype):
    print("receive message from the server")
    # decode the message
    received_buffer=[]
    while True:
        tmp = socket.recv(1)
        received_buffer+=tmp
        message_size,byte_read = _DecodeVarint32(received_buffer, 0)
        # print(message_size)
        # print(byte_read)
        if byte_read!=0:
            break

    # # receive the buffer
    received_buffer=socket.recv(message_size)
    # print(received_buffer)
    received_message=messagetype()
    received_message.ParseFromString(received_buffer)
    print("message received is: ")
    print(received_message)
    # print(received_message)
    return received_message

# def amazon_ups_init(amazon_ups_socket):

# initialize connection between amazon and world
# return the ------connection indicator---------
# to check if the connection is successfully established
def amazon_world_init(amazon_world_socket,world_id):
    print("initialize the communication between amazon and world\n")
    # message sent
    connect_message_sent=world.AConnect()
    connect_message_sent.isAmazon = True  # Set the value of isAmazon field
    # only one warehouse exists
    initwh = world.AInitWarehouse()
    initwh.id = 1
    initwh.x = 12
    initwh.y = 12
    connect_message_sent.initwh.append(initwh)    # -------------to add
    print(world_id)
    connect_message_sent.worldid = world_id
    print(connect_message_sent)
    
    # send message to the world
    send_message_to(amazon_world_socket,connect_message_sent) 

    # receive message from the world
    received_message=receive_message_from(amazon_world_socket,world.AConnected)

    print(received_message)
    # also check if connection is successfullt established
    if received_message.result=='connected!':
        return 1
    else:
        return 0
    
def amazon_ups_init(amazon_ups_socket):
    print("amazon_ups_init")
    # receive id from ups
    world_id=0
    world_id=receive_message_from(amazon_ups_socket,au.Connect).worldid

    # send back message if successfully connected
    if world_id!=0:
        connected_message_sent=au.Connected()
        connected_message_sent.result=True
        #-------------TODO: get from db---------------
        initwh=au.InitWarehouse()
        initwh.id = 1
        initwh.x = 12
        initwh.y = 12
        connected_message_sent.initwh.append(initwh)
        print(au.Connected)
        send_message_to(amazon_ups_socket,connected_message_sent)
    
    return world_id


def connect_to_web(HOST,PORT):
    # HOST = ''  # 监听所有的网络接口

    # 创建socket对象
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'Socket created')

    # 绑定套接字到指定的主机和端口
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()

    print(f'Socket bind complete')


    # 开始监听, 最大连接数为1
    s.listen(1)
    print(f'Socket now listening')

    return s

def keep_listen_to_web(socket):

    # while True:
    # accept connections from outside
    (client_socket, client_address) = socket.accept()
    print(f"Accepted connection from {client_address}")

    # receive message from client
    while True:
        whole_message = client_socket.recv(1024)
        if whole_message:
            print(f"Received message from {client_address}: {whole_message.decode()}")
            break

    # decoded_message = 
    # var_int_buff = []
    # while True:
    #     buf = client_socket.recv(1)
    #     var_int_buff += buf
    #     msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
    #     if new_pos != 0:
    #         break
    # whole_message = client_socket.recv(msg_len)
    # print(f"Received message from {client_address}: {whole_message.decode()}")
    # print(int(whole_message.decode()))
    return whole_message.decode()

    # close the connection
    # client_socket.close()
    # print(f"Closed connection from {client_address}")


# to do: communication with databae/front end
def connect_to_database():
    pass


    


    
     





     

