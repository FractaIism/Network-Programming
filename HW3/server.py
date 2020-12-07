#!/usr/bin/env python3

from modules import *
from params import *
import socket, threading, sqlite3, time

def main():
    try:
        # set up database
        sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.executescript('''
            CREATE TABLE users (
                username  TEXT  PRIMARY KEY  NOT NULL,
                password  TEXT,
                email     TEXT
            );
            CREATE TABLE sessions (
                session_id  INT  PRIMARY KEY,
                username  TEXT
            );
            CREATE TABLE boards (
                idx  INTEGER  PRIMARY KEY  AUTOINCREMENT,
                name   TEXT,
                moderator  TEXT
            );
            CREATE TABLE posts (
                serial_number  INTEGER  PRIMARY KEY  AUTOINCREMENT,
                board   TEXT,
                title   TEXT,
                content TEXT,
                author  TEXT,
                date    DATETIME  DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE comments (
                idx    INTEGER  PRIMARY KEY  AUTOINCREMENT,
                post_sn  INT,
                content  TEXT,
                author   TEXT
            );
        ''')
        sqlite_conn.commit()
        # open a TCP and a UDP port to accept commands for both protocols
        threading.Thread(target = TCP_listener).start()
        threading.Thread(target = UDP_listener).start()
        while True:
            time.sleep(10)  # keep thread alive so memory database doesn't get deleted
    except socket.error as se:
        print("Socket error: ", se)
    except Exception:
        ExceptionInfo()

def TCP_listener():
    try:
        ssock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssock_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ssock_tcp.bind((host, port))
        ssock_tcp.listen(10)
        print("TCP socket created, waiting for connections...")
        # await client connections (use separate thread for each connection)
        while True:
            (conn, addr) = ssock_tcp.accept()
            print("Connection established: ", addr)
            thread = threading.Thread(target = parseCommandTCP, args = (conn, addr))
            thread.start()
    except Exception:
        ExceptionInfo()

def UDP_listener():
    try:
        ssock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ssock_udp.bind((host, port))
        print("UDP socket created, waiting for connections...")
        # await client command (use separate thread for each command)
        while True:
            data, addr = ssock_udp.recvfrom(bufsize)
            thread = threading.Thread(target = parseCommandUDP, args = (data, addr))
            thread.start()
    except Exception:
        ExceptionInfo()

def parseCommandTCP(tcp_conn: socket.socket, addr):
    # data structure to store variables to pass into modules
    sv = SharedVariables()
    # static (non-changing) variables
    sv.tcp_conn = tcp_conn
    sv.addr = addr
    sv.sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    sv.sqlite_conn.isolation_level = None  # autocommit mode
    sv.sqlite_cursor = sv.sqlite_conn.cursor()
    # dynamic variables
    sv.session_id = -1  # -1 when not logged in, positive int when logged in
    sv.username = None  # None when not logged in

    # BBS commands, update this dict when commands are added/changed/deleted
    command_map = {
        "login"       : login,
        "logout"      : logout,
        "list-user"   : list_user,
        "create-board": create_board,
        "list-board"  : list_board,
        "create-post" : create_post,
        "update-post" : update_post,
        "delete-post" : delete_post,
        "list-post"   : list_post,
        "read"        : read,
        "comment"     : comment,
        "exit"        : client_exit,
        "help"        : command_list,
    }

    # bind SharedVariables object to each command function
    # for (cmd_name, cmd_func) in command_map.items():
    #     command_map[cmd_name] = functools.partial(cmd_func, sv)

    while True:  # keep serving until client exits
        try:
            # receive command from client
            data = tcp_conn.recv(bufsize)
            if not data:
                raise ConnectionError("Connection force closed by peer.")
            input_str = data.decode()
            sv.argv = str(input_str).split()
            sv.argc = len(sv.argv)
            command = sv.argv[0]
            print('parse TCP: ', sv.argv)
            if command in command_map:
                command_map[command](sv)
            else:
                # unused, handled on client side
                raise RuntimeError(886068, f"Unknown command '{command}'.")
            print(command+" success")

        except RuntimeError as err:
            # raise RuntimeError to print error on both client and server
            (errcode, errmsg) = err.args
            ExceptionInfo(errmsg)
            sv.tcp_conn.send(MSG_Encode(errcode, errmsg))
        except ConnectionError:
            ExceptionInfo()
            sv.sqlite_conn.close()
            tcp_conn.close()
            return
        # except Exception as e:
        #     ExceptionInfo()
        pass

# parse and serve one client request
def parseCommandUDP(data, addr):
    # data structure to store variables to pass into modules
    sv = SharedVariables()
    # static (non-changing) variables
    sv.udp_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv.udp_conn.connect(addr)
    sv.addr = addr
    sv.sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    sv.sqlite_conn.isolation_level = None  # autocommit mode
    sv.sqlite_cursor = sv.sqlite_conn.cursor()

    # receive command from client
    command = data.decode()
    sv.argv = str(command).split()
    sv.argc = len(sv.argv)
    command = sv.argv[0]
    print('parse UDP: ', sv.argv)

    try:
        if command == 'register':
            register(sv)
        elif command == 'whoami':
            whoami(sv)

    except RuntimeError as err:
        (errcode, errmsg) = err.args
        ExceptionInfo(errmsg)
        sv.udp_conn.send(MSG_Encode(errcode, errmsg))
    except ConnectionError:
        ExceptionInfo()
        sv.udp_conn.close()
        exit()
    except Exception:
        ExceptionInfo()
    pass

if __name__ == '__main__':
    main()
