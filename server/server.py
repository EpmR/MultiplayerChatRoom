import response_protocol
from server_socket import ServerSocket
from socket_wrapper import SocketWrapper
from threading import Thread
from config import *
from response_protocol import *
from db import DB


class Server:

    def __init__(self):
        self.server_socket = ServerSocket()

        # 创建调用请求的ID的字典
        self.request_handle_function = {}
        self.register(REQUEST_LOGIN, self.request_login_handle)
        self.register(REQUEST_CHAT, self.request_chat_handle)

        # 创建保存当前登录用户的字典
        self.clients = {}

        # 创建数据库管理对象
        self.db = DB()

    def remove_offline_user(self, client_soc):
        """移除离线用户连接"""
        username = None
        for uname, csock in self.clients.items():
            if csock['sock'].sock == client_soc.sock:
                username = uname

        # 删除用户信息
        del self.clients[username]

    def register(self, request_id, handle_function):
        """注册消息类型和处理函数到字典"""
        self.request_handle_function[request_id] = handle_function

    def startup(self):
        """多个客户端连接"""
        while True:
            # 获取客户端连接（套接字和IP地址）
            print('正在获取客户端连接...')
            soc, addr = self.server_socket.accept()
            print('获取到客户端连接！')

            # 调用socket_wrapper包装对象类
            client_soc = SocketWrapper(soc)

            # 创建子线程
            Thread(target=lambda: self.request_handle(client_soc)).start()

    def request_handle(self, client_soc):
        """处理客户端请求"""
        while True:
            # 收发消息
            recv_data = client_soc.recv_data()
            if not recv_data:
                remove_offline_user(client_soc)
                client_soc.close()
                break

            # 解析消息内容
            parse_data = parse_request_text(recv_data)

            # 分析请求类型，调用相应的函数
            handle_function = self.request_handle_function.get(parse_data['request_id'])
            if handle_function:
                handle_function(client_soc, parse_data)

    def request_login_handle(self, client_soc, request_data):
        """处理登录功能"""
        print('收到登录请求，准备处理...')

        # 获取账号密码
        username = request_data['username']
        password = request_data['password']

        # 检查是否能够登录
        ret, nickname, username = self.check_user_login(username, password)

        # 登录成功保存当前用户
        if ret == '1':  # 1要引号
            self.clients[username] = {'sock': client_soc, 'nickname': nickname}

        # print(self.clients)

        # 拼接返回给客户端的消息
        response_text = response_protocol.response_login_result(ret, nickname, username)

        # 把消息发送给客户端
        client_soc.send_data(response_text)

    def check_user_login(self, username, password):
        """检查用户是否登陆成功，并返回检查结果（0失败，1成功），昵称，用户账号"""
        # 从数据库查询用户信息
        result = self.db.get_one("select * from users where user_name ='%s'" % username)

        # 没有查询结果，用户不存在，登陆失败
        if not result:
            return '0', '', username

        # 密码不正确，登陆失败
        if password != result['user_password']:
            return '0', '', username

        # 登陆成功
        return '1', result['user_nickname'], username

    def request_chat_handle(self, client_soc, request_data):
        """处理聊天功能"""
        print('收到聊天信息，准备处理...')

        # 获取消息内容
        username = request_data['username']
        messages = request_data['messages']
        nickname = self.clients[username]['nickname']

        # 拼接发送给客户端消息文本
        msg = response_protocol.response_chat(nickname, messages)

        # 转发给在线用户
        for u_name, info in self.clients.items():   # 先u_name，再info，键值写反出现字符串索引必须是整数的错误
            # 不需要向发送消息的账号转发数据
            if username == u_name:
                continue
            info['sock'].send_data(msg)


def remove_offline_user(client_soc):
    """客户下线通知"""
    print('有客户端下线了...')


def parse_request_text(text):
    """
    解析发过来的请求
    登录信息：0001|username|password
    聊天信息：0002|username|messages
    """
    print('解析客户端数据：' + text)
    request_list = text.split(DELIMITER)
    request_data = {'request_id': request_list[0]}

    # 用户请求登录
    if request_data['request_id'] == REQUEST_LOGIN:
        request_data['username'] = request_list[1]
        request_data['password'] = request_list[2]

    # 用户请求聊天
    elif request_data['request_id'] == REQUEST_CHAT:
        '''用户请求聊天'''
        request_data['username'] = request_list[1]
        request_data['messages'] = request_list[2]

    return request_data


if __name__ == '__main__':
    Server().startup()
