#!/usr/bin/python3
import socket, threading, sqlite3, inspect, json, os, time, sys, random

arg_c = len(sys.argv)

host = ''  # bind to this machine
port = 9746 if arg_c < 2 else int(sys.argv[1])
sqlite_db = 'file:nphw2?mode=memory&cache=shared'
bufsize = 4096

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
            pass  # keep thread alive so memory database doesn't get deleted
    except socket.error as se:
        print("Socket error: ", se)
    except Exception as e:
        ExceptionInfo()

def TCP_listener():
    try:
        # print("TCP listener")
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
    except KeyboardInterrupt as kb:
        print("Server process terminated.")
        ssock_tcp.close()
        exit()
    except Exception as e:
        ExceptionInfo()

def UDP_listener():
    try:
        # print("UDP listener")
        ssock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ssock_udp.bind((host, port))
        print("UDP socket created, waiting for connections...")
        # await client command (use separate thread for each command)
        while True:
            data, addr = ssock_udp.recvfrom(bufsize)
            thread = threading.Thread(target = parseCommandUDP, args = (data, addr))
            thread.start()
    except KeyboardInterrupt as kb:
        print("Server process terminated.")
        ssock_udp.close()
        exit()
    except Exception as e:
        ExceptionInfo()

def parseCommandTCP(tcp_conn: socket.socket, addr):
    # sqlite
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    sqlite_conn.isolation_level = None  # autocommit mode
    sqlite_cursor = sqlite_conn.cursor()

    session_id = -1  # -1 when not logged in, positive int when logged in
    username = None  # None when not logged in
    while True:  # keep serving until client logs out
        try:
            # receive command from client
            data = tcp_conn.recv(bufsize)
            if not data:
                raise ConnectionError("Connection force closed by peer.")
            input_str = data.decode()
            argv = str(input_str).split()
            argc = len(argv)  # not needed, syntax check done on client side
            command = argv[0]
            print('parse TCP: ', argv)

            if command == 'login':
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
                obj = {
                    'session_id': session_id,
                    'message'   : f"Welcome, {credentials[0]}."
                }
                tcp_conn.send(MSG_Encode(0, json.dumps(obj)))
                print('login success')

            elif command == 'logout':
                # destroy session
                sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [session_id])
                session_id = -1
                username = None
                print('logout success')

            elif command == 'list-user':
                records = sqlite_cursor.execute('SELECT username,email FROM users')
                user_list = []
                for rec in records:
                    user_list.append(rec)
                tcp_conn.send(MSG_Encode(0, json.dumps(user_list)))
                print(user_list)
                print("list-user success")

            elif command == 'create-board':
                board_name = argv[1]
                exist_check = sqlite_cursor.execute("SELECT * FROM boards WHERE name = ? ", [board_name])
                if len(exist_check.fetchall()) > 0:
                    errmsg = "Board already exists."
                    tcp_conn.send(MSG_Encode(57238, errmsg))
                    raise Exception(errmsg)
                sqlite_cursor.execute("INSERT INTO boards (name, moderator) VALUES (?,?) ", [board_name, username])
                tcp_conn.send(MSG_Encode(0, "Create board successfully."))
                print("create-board success")

            elif command == 'list-board':
                records = sqlite_cursor.execute("SELECT * FROM boards")
                tcp_conn.send(MSG_Encode(0, json.dumps(list(records))))
                print("list-board success")

            elif command == 'create-post':
                (board, title) = (argv[1], argv[3])
                n = 4
                while n < argc and argv[n] != "--content":
                    title = f"{title} {argv[n]}"
                    n = n + 1
                n = n + 1
                content = ""
                while n < argc:
                    content = f"{content} {argv[n]}"
                    n = n + 1
                print(board, title, content)
                sqlite_cursor.execute("INSERT INTO posts (board, title, content, author) VALUES (?,?,?,?) ",
                                      [board, title, content, username])
                tcp_conn.send(MSG_Encode(0, "Create post successfully."))
                print("create-post success")

            elif command == 'update-post':
                post_sn = argv[1]
                if argv[2] == '--title':
                    field = 'title'
                elif argv[2] == '--content':
                    field = 'content'
                else:
                    raise Exception("Invalid field")
                newdata = " ".join(argv[3:])
                sqlite_cursor.execute(f"UPDATE posts SET {field} = ? WHERE serial_number = ? ", [newdata, post_sn])
                tcp_conn.send(MSG_Encode(0, "Update post successfully."))
                print("update-post success")
                DebugDB('posts')

            elif command == 'delete-post':
                post_sn = argv[1]
                sqlite_cursor.execute("DELETE FROM posts WHERE serial_number = ? ", [post_sn])
                tcp_conn.send(MSG_Encode(0, "Delete post successfully."))
                print("delete-post success")
                DebugDB('posts')

            elif command == 'list-post':
                board = argv[1]
                posts = sqlite_cursor.execute("SELECT serial_number, title, author, date FROM posts WHERE board = ? ",
                                              [board])
                tcp_conn.send(MSG_Encode(0, json.dumps(list(posts))))
                print("list-post success")

            elif command == 'read':
                DebugDB('posts')
                post_sn = argv[1]
                post = []
                post_info = sqlite_cursor.execute(
                        "SELECT author, title, date, content FROM posts WHERE serial_number = ? ", [post_sn])
                post.append(post_info.fetchone())
                comments = sqlite_cursor.execute("SELECT author, content FROM comments WHERE post_sn = ? ORDER BY idx",
                                                 [post_sn])
                for comment in comments.fetchall():
                    post.append(comment)
                tcp_conn.send(MSG_Encode(0, json.dumps(post)))
                print("read success")

            elif command == 'comment':
                (post_sn, content) = (argv[1], " ".join(argv[2:]))
                sqlite_cursor.execute("INSERT INTO comments (post_sn, author, content) VALUES (?,?,?) ",
                                      [post_sn, username, content])
                tcp_conn.send(MSG_Encode(0, "Comment successfully."))
                print("comment success")
                DebugDB("comments")

            elif command == 'exit':
                sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [session_id])
                tcp_conn.close()
                print(f"User {addr} has exited.")
                return

            else:
                errmsg = f'''Unknown command '{command}'.
                             Command list:
                             register <username> <email> <password>
                             login <username> <password>
                             logout
                             whoami
                             list-user
                             create-board <name>
                             create-post <board-name> --title <title>
--content <content>
                             list-board
                             list-post <board-name>
                             read <post-S/N>
                             delete-post <post-S/N>
                             update-post <post-S/N> --title/content <new>
                             comment <post-S/N> <comment>
                             exit'''
                tcp_conn.send(errmsg.encode())
                raise Exception(errmsg)

        except KeyboardInterrupt:
            print("Server process terminated.")
            tcp_conn.close()
            exit()
        except ConnectionError:
            ExceptionInfo()
            tcp_conn.close()
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
        sqlite_conn.isolation_level = None  # autocommit mode
        sqlite_cursor = sqlite_conn.cursor()
        # receive command from client
        command = data.decode()
        argv = str(command).split()
        argc = len(argv)
        command = argv[0]
        print('parse UDP: ', argv)

        if command == 'register':
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

        elif command == 'whoami':
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

    except KeyboardInterrupt:
        print("Server process terminated.")
        socket_udp.close()
        exit()
    except ConnectionError:
        ExceptionInfo()
        socket_udp.close()
        exit()
    except Exception as e:
        ExceptionInfo()

# print exception info and line number
def ExceptionInfo():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    funcname = inspect.currentframe().f_back.f_code.co_name
    # print("Exception info: ", exc_type, filename, funcname, exc_tb.tb_lineno,exc_obj)
    print("Exception caught:", exc_type, exc_obj)
    print("Exception at:", filename, funcname, exc_tb.tb_lineno)

# view database contents
def DebugDB(table = "*"):
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    if table == "*":
        table = ["boards", "posts", "comments"]
    if not isinstance(table, list):
        table = [table]

    print()
    print(f"DebugDB: {table}")
    for tab in table:
        print(f"TABLE {tab}:")
        columns = sqlite_conn.execute(f"PRAGMA table_info({tab})")
        col_names = []
        for col in columns:
            col_names.append(col[1])
        print(col_names)
        records = sqlite_conn.execute(f"SELECT * FROM {tab}")
        for rec in records:
            print(rec)
        print()

def MSG_Encode(retcode: int, message: str = "Default message"):
    pkg = {
        'retcode': retcode,
        'message': message
    }
    return json.dumps(pkg).encode()

# exc_hook_args = {'exc_type': type(Exception), 'exc_value': Exception("Server process completed."),
#                  'exc_traceback': None, 'thread': None}

if __name__ == '__main__':
    main()
