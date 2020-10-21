import socket, threading, sqlite3, inspect, json, os, time, sys, random

host = ''  # bind to this machine
TCP_port = 6573
# UDP_port = 7923
UDP_port = 6573
sqlite_db = 'mydb.db'
bufsize = 4096

def main():
    try:
        # start with clean up database
        db_abs = os.path.realpath(__file__)
        os.chdir(os.path.dirname(db_abs))
        if os.path.exists(sqlite_db):
            os.remove(sqlite_db)
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
        ''')
        sqlite_conn.commit()
        # open a TCP and a UDP port to accept commands for both protocols
        threading.Thread(target = TCP_listener).start()
        threading.Thread(target = UDP_listener).start()
    except socket.error as se:
        print("Socket error: ", se)
    except Exception as e:
        ExceptionInfo()

def TCP_listener():
    try:
        # print("TCP listener")
        ssock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssock_tcp.bind((host, TCP_port))
        ssock_tcp.listen(5)
        print("TCP socket created, waiting for connections...")
        # await client connections (use separate thread for each connection)
        while True:
            (conn, addr) = ssock_tcp.accept()
            print("Connection established: ", addr)
            thread = threading.Thread(target = parseCommandTCP, args = (conn, addr))
            thread.start()
    except KeyboardInterrupt as kb:
        print("Server process terminated.")
        exit()
    except Exception as e:
        ExceptionInfo()

def UDP_listener():
    try:
        # print("UDP listener")
        ssock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock_udp.bind((host, UDP_port))
        print("UDP socket created, waiting for connections...")
        # await client command (use separate thread for each command)
        while True:
            data, addr = ssock_udp.recvfrom(bufsize)
            thread = threading.Thread(target = parseCommandUDP, args = (data, addr))
            thread.start()
    except KeyboardInterrupt as kb:
        print("Server process terminated.")
        exit()
    except Exception as e:
        ExceptionInfo()

def parseCommandTCP(tcp_conn, addr):
    # sqlite
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    sqlite_conn.isolation_level = None
    sqlite_cursor = sqlite_conn.cursor()

    session_id = -1  # -1 when not logged in, positive int when logged in
    username = None  # None when not logged in
    while True:  # keep serving until client logs out
        try:
            # receive command from client
            data = tcp_conn.recv(bufsize)
            if not data:
                raise Exception("Connection closed by peer")
            command = data.decode()
            argv = str(command).split()
            argc = len(argv)  # not needed, syntax check done on client side
            print('parse TCP: ', argv)

            if argv[0] == 'login':
                sqlite_cursor.execute('SELECT username,password FROM users WHERE username = ?', [argv[1]])
                credentials = sqlite_cursor.fetchone()
                # check if user exists
                if credentials is None:
                    tcp_conn.send(MSG_Encode(78264))
                    raise Exception("Login failed. User does not exist.")
                # check if password matches
                if credentials[1] != argv[2]:
                    tcp_conn.send(MSG_Encode(78264))
                    raise Exception("Login failed. Wrong password.")
                # login success
                session_id = random.randint(1, 9223372036854775807)
                username = credentials[0]
                sqlite_cursor.execute("INSERT INTO sessions (session_id,username) VALUES (?,?) ",
                                      [session_id, username])
                sqlite_conn.commit()
                obj = {'session_id': session_id, 'message': f"Welcome, {credentials[0]}."}
                tcp_conn.send(MSG_Encode(0, json.dumps(obj)))
                print('login success')

            elif argv[0] == 'logout':
                # destroy session
                sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [session_id])
                session_id = -1
                username = None
                print('logout success')

            elif argv[0] == 'list-user':
                records = sqlite_cursor.execute('SELECT username,email FROM users')
                user_list = []
                for rec in records:
                    user_list.append(rec)
                tcp_conn.send(MSG_Encode(0, json.dumps(user_list)))
                print(user_list)
                print("list-user success")

            elif argv[0] == 'exit':
                sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [session_id])
                tcp_conn.close()
                return

            else:
                errmsg = f'''Unknown command '{argv[0]}'.
                             Command list:
                             register <username> <email> <password>
                             login <username> <password>
                             logout
                             whoami
                             list-user
                             exit'''
                tcp_conn.send(errmsg.encode())
                raise Exception(errmsg)

        except KeyboardInterrupt as kb:
            print("Server process terminated.")
            exit()
        except Exception as e:
            ExceptionInfo()

# parse and serve one client request
def parseCommandUDP(data, addr):
    try:
        # general-purpose UDP socket
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socket_udp.connect(addr)
        # sqlite
        sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
        sqlite_conn.isolation_level = None
        sqlite_cursor = sqlite_conn.cursor()
        # receive command from client
        command = data.decode()
        argv = str(command).split()
        argc = len(argv)
        print('parse UDP: ', argv)

        if argv[0] == 'register':
            # check for duplicate username
            sqlite_cursor.execute('SELECT username FROM users WHERE username = ?', (argv[1],))
            if sqlite_cursor.fetchone() is not None:
                errmsg = "Username is already used."
                socket_udp.send(MSG_Encode(27387, errmsg))
                raise Exception(errmsg)
            # add user to database
            sqlite_cursor.execute("INSERT INTO users ('username','email','password') VALUES (?,?,?)",
                                  (argv[1], argv[2], argv[3]))
            sqlite_conn.commit()
            socket_udp.send(MSG_Encode(0, "Register success."))
            print("register success")

        elif argv[0] == 'whoami':
            session_id = argv[1]
            data1 = sqlite_cursor.execute(
                "SELECT username FROM users NATURAL JOIN sessions WHERE sessions.session_id = ? ", [session_id])
            user = data1.fetchone()[0]
            print(user)
            if user is not None:
                socket_udp.send(MSG_Encode(0, user))
                print("whoami success")
            else:
                errmsg = "IDK who I am"
                socket_udp.send(MSG_Encode(1847, errmsg))
                raise Exception(errmsg)  # socket_udp.send(MSG_Encode(0, "Debugging..."))

    except KeyboardInterrupt as kb:
        print("Server process terminated.")
        exit()
    except Exception as e:
        ExceptionInfo()

def ExceptionInfo():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    funcname = inspect.currentframe().f_back.f_code.co_name
    # print("Exception info: ", exc_type, filename, funcname, exc_tb.tb_lineno,exc_obj)
    print("Exception caught:", exc_type, exc_obj)
    print("Exception at:", filename, funcname, exc_tb.tb_lineno)

def MSG_Encode(retcode: int, message: str = "Default message"):
    pkg = {'retcode': retcode, 'message': message}
    return json.dumps(pkg).encode()

# exc_hook_args = {'exc_type': type(Exception), 'exc_value': Exception("Server process completed."),
#                  'exc_traceback': None, 'thread': None}

if __name__ == '__main__':
    main()
