import socket, json, sys

try:
    csockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    csockUDP.connect(('localhost', 7854))
    print(csockUDP)
except Exception as e:
    print("Exception: ", e)
