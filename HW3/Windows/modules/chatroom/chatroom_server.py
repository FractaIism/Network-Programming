from modules.utility import *
from params import bufsize
from typing import Dict, List
from datetime import datetime
import threading, socket

server_online = None  # type:bool
server_socket = None  # type:socket.socket
connection_list = {}  # type:Dict[str,socket.socket]
input_thread = None  # type:threading.Thread
attached = None  # type:bool
username = None  # type:str
message_log = []  # type:List[str]
status = ""  # type:str # "chatroom", "leave", "detach"

def chatroom_server(user: str, chatroom_port: int):
    global server_online, attached, input_thread, username, status, connection_list
    server_online = True
    attached = True
    connection_list = {}
    status = "chatroom"
    username = user
    input_thread = threading.Thread(target = get_input)
    listener_thread = threading.Thread(target = listener, args = [chatroom_port])
    # print(f"Created chatroom at port {chatroom_port}")
    print("*****************************")
    print("** Welcome to the chatroom **")
    print("*****************************")
    for msg in message_log[-3:]:
        print(msg)
    input_thread.start()
    listener_thread.start()

def listener(chatroom_port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', chatroom_port))
    server_socket.listen(5)
    try:
        # while chatroom owner keeps chatroom open, accept connection from peers
        while server_online:
            (conn, addr) = server_socket.accept()
            user = conn.recv(bufsize).decode()
            connection_list[user] = conn
            threading.Thread(target = print_peer_msg, args = [conn, user]).start()
            conn.send(("xyz" + "\n".join(message_log[-3:])).encode())  # add random string to prevent sending nothing (not sending anything)
            # notify everyone of newly joined user
            join_msg = datetime.now().strftime(f"sys [%H:%M] : {user} has joined us.")
            if attached:
                print(join_msg)
            for peer_conn in connection_list.values():
                if peer_conn != conn:
                    peer_conn.send(join_msg.encode())
    except OSError:
        # chatroom server socket closed, accept fails
        pass

# get input from local user and send to all peers
def get_input():
    global server_online, status
    while server_online:
        input_str = input()
        # parse commands first
        if input_str == 'leave-chatroom':
            global server_socket
            server_online = False
            status = "leave"
            for peer_conn in connection_list.values():
                peer_conn.close()
            server_socket.close()
            return
        elif input_str == 'detach':
            global attached
            attached = False
            status = "detach"
            return
        elif input_str.strip() != '':  # if nonempty, send as plain text
            global username
            fmsg = datetime.now().strftime(f"{username} [%H:%M] : {input_str}")  # formatted message
            message_log.append(fmsg)
            for conn in connection_list.values():
                conn.send(fmsg.encode())

# recv messages from each user (one thread per user) and print it, then forward it to all peers
def print_peer_msg(conn: socket.socket, user: str):
    global server_online, attached
    try:
        while server_online:
            msg = conn.recv(bufsize)
            message_log.append(msg.decode())
            if attached:
                print(msg.decode())
            for peer_conn in connection_list.values():
                if peer_conn != conn:
                    peer_conn.send(msg)
    except ConnectionResetError:
        # peer left chatroom
        msg = datetime.now().strftime(f"sys [%H:%M] : {user} leave us.")
        if attached:
            print(msg)
        connection_list.pop(user)
        for peer_conn in connection_list.values():
            peer_conn.send(msg.encode())
    except ConnectionAbortedError:
        # chatroom owner left chatroom
        pass

def attach():
    global attached, status, input_thread
    print("*****************************")
    print("** Welcome to the chatroom **")
    print("*****************************")
    attached = True
    status = "chatroom"
    for msg in message_log[-3:]:
        print(msg)
    input_thread = threading.Thread(target = get_input)
    input_thread.start()
