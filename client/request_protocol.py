from config import *


class RequestProtocol:

    @staticmethod
    def request_login_result(username, password):
        """0001|user1|111111"""
        return DELIMITER.join([REQUEST_LOGIN, username, password])

    @staticmethod
    def request_chat(username, message):
        """0002|user1|msg"""
        return DELIMITER.join([REQUEST_CHAT, username, message])
