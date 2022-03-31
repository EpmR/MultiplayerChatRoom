import socket


def test():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client_socket.connect(('127.0.0.1', 65535))

    while True:
        message = input('输入发送的数据：')
        client_socket.send(message.encode('utf-8'))
        recv_data = client_socket.recv(512)
        print(recv_data.decode('utf-8'))


if __name__ == '__main__':
    test()
