import socket
from config import *


class ClientSocket(socket.socket):
    """客户端套接字的自定义处理"""

    def __init__(self):
        # 设置为TCP套接字
        super(ClientSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """自动连接到服务器"""
        super(ClientSocket, self).connect((SERVER_IP, SERVER_PORT))

    def recv_data(self):
        """接收数据，并自动转换为字符串输出"""
        return self.recv(512).decode('utf-8')

    def send_data(self, message):
        """接收一个字符串，并转换为字节数据发送"""
        return self.send(message.encode('utf-8'))

