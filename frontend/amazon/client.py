import socket


def sendMsg(message):
    # HOST = '127.0.0.1'  # 服务端IP地址
    # HOST = socket.gethostname()
    HOST = 'vcm-30735.vm.duke.edu'
    PORT = 8888  # 服务端端口号

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
    except socket.error as e:
        print(f"Error connecting to server: {e}")
        return

    try:
        client_socket.sendall(message.encode())
    except socket.error as e:
        print(f"Error sending message: {e}")
    finally:
        client_socket.close()
    
    # # 创建socket对象
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client_socket.connect((HOST, PORT))

    # # 发送消息到服务器
    # client_socket.sendall(message.encode())

    # # 关闭客户端 socket
    client_socket.close()

# Receive message(Only once)    
def recvMsg():
    HOST = socket.gethostname()
    PORT = 8888  # 服务端端口号

    # 创建socket对象
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 接收服务器的响应消息
    data = client_socket.recv(1024)

    # 关闭客户端 socket
    client_socket.close()

    return data.decode()

# TEST
#sendMsg(str(2))