#!/usr/bin/python3
import socket, json, sys

arg_c = len(sys.argv)

remoteHost = 'localhost' if arg_c < 2 else sys.argv[1]
remotePort = 9746 if arg_c < 3 else int(sys.argv[2])
bufsize = 1024

def MSG_Decode(bytestream: bytes):
    msg_str = bytestream.decode()
    msg = json.loads(msg_str)
    return msg['retcode'], msg['message']

session_id = -1
username = None
csockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
csockTCP.connect((remoteHost, remotePort))
csockUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# print(f"Connected to server at {remoteHost}:{remotePort}")
print("********************************\n** Welcome to the BBS server. **\n********************************")

while True:
    input_str = input('% ')
    argv = input_str.split()
    argc = len(argv)
    command = argv[0]

    if command == 'register':
        if argc != 4:
            print("Usage: register <username> <email> <password>")
            continue
        csockUDP.sendto(input_str.encode(), (remoteHost, remotePort))
        msg = csockUDP.recv(bufsize)
        (retcode, message) = MSG_Decode(msg)
        print(message)

    elif command == 'login':
        if argc != 3:  # check syntax
            print("Usage: login <username> <password>")
            continue
        elif session_id != -1:  # check login status
            print("Please logout first.")
            continue
        csockTCP.send(input_str.encode())
        msg = csockTCP.recv(bufsize)
        (retcode, message) = MSG_Decode(msg)
        if retcode == 78264:
            print("Login failed.")
            continue
        elif retcode == 0:
            obj = json.loads(message)
            session_id = obj['session_id']
            username = argv[1]
            msg = obj['message']
            print(msg)

    elif command == 'logout':
        if argc != 1:
            print("Usage: logout")
            continue
        elif session_id == -1:
            print("Please login first.")
            continue
        session_id = -1
        csockTCP.send(input_str.encode())
        print(f"Bye, {username}.")

    elif command == 'whoami':
        if argc != 1:
            print("Usage: whoami")
            continue
        elif session_id == -1:
            print("Please login first.")
            continue
        csockUDP.sendto(f"whoami {session_id}".encode(), (remoteHost, remotePort))
        msg = csockUDP.recv(bufsize)
        (retcode, message) = MSG_Decode(msg)
        if retcode == 1847:
            print("IDK who I am")
            continue
        print(message)

    elif command == 'list-user':
        csockTCP.send(input_str.encode())
        msg = csockTCP.recv(bufsize)
        (retcode, message) = MSG_Decode(msg)
        user_list = json.loads(message)
        # print('user_list=', user_list)
        print("{:<15} {:<15}".format("Username", "Email"))
        for user in user_list:
            print("{:<15} {:<15}".format(user[0], user[1]))

    elif command == 'exit':
        session_id = -1
        username = None
        csockTCP.send(input_str.encode())
        csockTCP.close()
        exit()

    elif command == 'help':
        print(
            f"Command list:\nregister <username> <email> <password>\nlogin <username> <password>\nlogout\nwhoami\nlist-user\nexit")

    else:  # unknown command
        print(f"Unknown command '{argv[0]}'. Type 'help' for the list of commands.")
