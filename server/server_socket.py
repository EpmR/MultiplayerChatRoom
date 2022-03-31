import socket
from config import *


class ServerSocket(socket.socket):

    def __init__(self):
        # 设置为TCP类型
        super(ServerSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)

        # 绑定地址端口号，为了方便修改，地址端口号放在config中
        self.bind((SERVER_IP, SERVER_PORT))

        # 设置为监听模式，允许128个主机连接
        self.listen(128)
