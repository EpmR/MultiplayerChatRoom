import sys
from tkinter.messagebox import showinfo
from window_chat import WindowChat
from window_login import WindowLogin
from request_protocol import RequestProtocol
from client_socket import ClientSocket
from threading import Thread
from config import *


class Client:

    def __init__(self):
        """初始化客户端资源"""
        # 初始化登录窗口
        self.window = WindowLogin()
        self.window.on_reset_button_click(self.clear_inputs)
        self.window.on_login_button_click(self.send_login_data)
        self.window.on_window_closed(self.exit)

        # 创建客户端套接字
        self.conn = ClientSocket()

        # 初始化消息处理函数
        self.response_handle_function = {RESPONSE_LOGIN_RESULT: self.response_login_handle,
                                         RESPONSE_CHAT: self.response_chat_handle}

        # 初始化聊天窗口
        self.window_chat = WindowChat()
        self.window_chat.withdraw()  # 隐藏窗口
        self.window_chat.on_send_button_click(self.send_chat_data)
        self.window_chat.on_window_closed(self.exit)

        # 在线用户名
        self.username = None

        # 程序正在运行的标记
        self.is_running = True

    def startup(self):
        """开启窗口"""
        self.conn.connect()
        Thread(target=self.response_handle).start()
        self.window.mainloop()

    def clear_inputs(self):
        """清空窗口内容"""
        self.window.clear_username()
        self.window.clear_password()

    def send_login_data(self):
        """发送登录信息到服务器"""
        # 获取到输入的账号密码
        username = self.window.get_username()
        password = self.window.get_password()

        # 生成协议文本
        request_text = RequestProtocol.request_login_result(username, password)

        # 发送协议文本到服务器
        self.conn.send_data(request_text)

    def send_chat_data(self):
        """获取输入框内容，发送到服务器"""
        # 获取输入
        message = self.window_chat.get_inputs()
        self.window_chat.clear_input()  # 发送完一条消息需要清空输入框

        # 拼接协议文本
        request_text = RequestProtocol.request_chat(self.username, message)

        # 发送消息内容
        self.conn.send_data(request_text)

        # 把消息内容显示到聊天区
        self.window_chat.append_message('我', message)

    def response_handle(self):
        """不断接受服务器消息"""
        while self.is_running:
            # 获取服务器消息
            recv_data = self.conn.recv_data()
            print('收到服务器消息：' + recv_data)

            # 解析消息内容
            response_data = self.parse_response_data(recv_data)

            # 根据消息内容进行处理
            handle_function = self.response_handle_function[response_data['response_id']]

            if handle_function:
                handle_function(response_data)

    @staticmethod
    def parse_response_data(recv_data):

        # 使用协议约定的符号来切个消息
        response_data_list = recv_data.split(DELIMITER)

        # 解析消息的组成部分
        response_data = {'response_id': response_data_list[0]}

        if response_data['response_id'] == RESPONSE_LOGIN_RESULT:
            response_data['result'] = response_data_list[1]
            response_data['nickname'] = response_data_list[2]
            response_data['username'] = response_data_list[3]

        elif response_data['response_id'] == RESPONSE_CHAT:
            response_data['nickname'] = response_data_list[1]
            response_data['message'] = response_data_list[2]

        return response_data

    def response_login_handle(self, response_data):
        """登录结果响应"""
        print('接收到登录消息', response_data)
        result = response_data['result']
        if result == '0':
            showinfo('提示', '登陆失败，账号或密码错误')
            print('登陆失败')
            return

        # 登陆成功获取用户信息
        nickname = response_data['nickname']
        self.username = response_data['username']   # 保存登录用户的账号，供发消息使用

        # 显示聊天窗口
        self.window_chat.set_title(nickname)
        self.window_chat.update()
        self.window_chat.deiconify()

        # 隐藏登录窗口
        self.window.withdraw()

    def response_chat_handle(self, response_data):
        """聊天信息响应"""
        print('接收到聊天消息', response_data)
        message = response_data['message']
        sender = response_data['nickname']
        self.window_chat.append_message(sender, message)

    def exit(self):
        """退出程序"""
        self.is_running = False
        self.conn.close()
        sys.exit()


if __name__ == '__main__':
    client = Client()
    client.startup()
