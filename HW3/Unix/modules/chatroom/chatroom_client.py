from params import bufsize
from typing import Tuple
from datetime import datetime
import threading, socket, sys

connected = None  # type:bool
last_msg = None  # type:str # treat last msg as BBS command
input_thread = None  # type: threading.Thread # to .join() with after chatroom server closes
safeDC = None  # true if leave using leave-chatroom, false if chatroom server closes

def chatroom_client(username: str, chatroom_addr: Tuple[str, int]):
    global connected, input_thread, safeDC, last_msg
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.connect(chatroom_addr)
    client_socket.send(username.encode())  # send username to let chatroom server identify us
    connected = True
    safeDC = False
    last_msg = None
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
        global connected, safeDC
        while connected:
            input_str = input()
            if connected:
                if input_str == 'leave-chatroom':
                    connected = False
                    safeDC = True
                    conn.close()
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
        conn.setblocking(False)
        while True:
            try:
                msg = conn.recv(bufsize)
            except BlockingIOError:
                # conn.recv got no message
                continue
            if msg == b'':  # when chatroom server closes
                raise OSError
            print(msg.decode())
    except OSError:  # used to be ConnectionResetError with blocking recv on Windows, now use OSError with nonblocking recv
        # chatroom owner has left
        global connected
        print(datetime.now().strftime(f"sys [%H:%M] : the chatroom is closed."))
        print("Welcome back to BBS.")
        if connected:  # print prompt only if chatroom server closed connection
            print("%", end = " ")
        sys.stdout.flush()  # necessary on linux, otherwise execution stops before "if connected:" WTF?
        connected = False
    except ConnectionAbortedError:
        # local user has left
        pass
