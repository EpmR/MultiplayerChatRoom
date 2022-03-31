from config import *


class response_protocol:
    """通信数据协议字符串处理"""

    @staticmethod
    def response_login_result(result, nickname, username):  # 这3个传参
        """
        生成登录字符串
        :param result: 登陆成功值为1，失败值为0
        :param nickname:
        :param username:
        :return:
        """
        return DELIMITER.join([RESPONSE_LOGIN_RESULT, result, nickname, username])

    @staticmethod
    def response_chat(nickname, messages):
        """
        :param nickname:
        :param messages:
        :return:
        """
        return DELIMITER.join([REQUEST_CHAT, nickname, messages])
