# import socket

UDP_IP = "172.10.24.30"
UDP_PORT = "516"
MESSAGE = "TEST|MDP from Python"

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
# sock.connect((UDP_IP, UDP_PORT))
# sock.send(MESSAGE.encode())
# sock.recv(5)

import os

os.system(f'echo -n "{MESSAGE}" | nc -w5 -u {UDP_IP} {UDP_PORT}')
