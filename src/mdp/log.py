from socket import socket, AF_INET, SOCK_DGRAM
import environ

env = environ.Env()


class Log:
    def __init__(self):
        self.s = socket(AF_INET, SOCK_DGRAM, 0)

    def __call__(self, msg):
        msg = f"<1>{msg}".encode('utf-8')
        self.s.sendto(msg, (env("LOG_SERVER"), int(env("LOG_PORT"))))
