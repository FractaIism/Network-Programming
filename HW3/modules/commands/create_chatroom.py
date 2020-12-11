from modules.utility import *

# treat syntax as create-chatroom <port> <host>, since <host> is automatically appended on the client side
syntax = "Usage: create-chatroom <port>"

def create_chatroom(sv: SharedVariables):
    # check syntax
    if sv.argc < 3:
        raise RuntimeError(508797, syntax)
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(62502, "Please login first.")
    # check if chatroom exists
    sv.sqlite_cursor.execute("SELECT * FROM chatrooms WHERE name = ? ", [sv.username])
    if sv.sqlite_cursor.fetchone() is not None:
        raise RuntimeError(794882, "User has already created the chatroom.")
    else:
        (host, port) = (sv.argv[2], sv.argv[1])
        sv.sqlite_cursor.execute("INSERT INTO chatrooms (name,host,port,status) VALUES (?,?,?,?) ", [sv.username, host, port, 'open'])
        DebugDB('chatrooms')
        sv.tcp_conn.send(MSG_Encode(0, "Start to create chatroom..."))
