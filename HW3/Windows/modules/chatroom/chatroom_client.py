from params import bufsize
from typing import Tuple
from datetime import datetime
import threading, socket

connected = None  # type:bool
last_msg = None  # type:str # treat last msg as BBS command
input_thread = None  # type: threading.Thread # to .join() with after chatroom server closes

def chatroom_client(username: str, chatroom_addr: Tuple[str, int]):
    global connected, input_thread
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect(chatroom_addr)
    client_socket.send(username.encode())  # send username to let chatroom server identify us
    connected = True
    input_thread = threading.Thread(target = get_input, args = [client_socket, username])
    output_thread = threading.Thread(target = print_peer_msg, args = [client_socket])
    # print(f"Connected to chatroom at {chatroom_addr}")
    print("*****************************")
    print("** Welcome to the chatroom **")
    print("*****************************")
    prev_messages = client_socket.recv(bufsize).decode()[3:]
    if prev_messages != '':
        for msg in prev_messages.split('\n'):
            print(msg)
    input_thread.start()
    output_thread.start()

# get input from local user and send to all peers
def get_input(conn: socket.socket, username: str):
    input_str = None
    try:
        global connected
        while connected:
            input_str = input()
            if connected:
                if input_str == 'leave-chatroom':
                    connected = False
                    conn.close()
                    print("Welcome back to BBS.")
                    return
                elif input_str.strip() != '':
                    msg = datetime.now().strftime(f"{username} [%H:%M] : {input_str}")
                    conn.send(msg.encode())
            else:
                raise ConnectionResetError
    except ConnectionResetError:
        global last_msg
        last_msg = input_str

# recv messages from each user and print it
def print_peer_msg(conn: socket.socket):
    try:
        while True:
            msg = conn.recv(bufsize)
            print(msg.decode())
    except ConnectionResetError:
        # chatroom owner has left
        global connected
        connected = False
        print(datetime.now().strftime(f"sys [%H:%M] : the chatroom is closed."))
        print("Welcome back to BBS.")
        print("%", end = " ")
    except ConnectionAbortedError:
        # local user has left
        pass
