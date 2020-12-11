from modules.utility import *

syntax = "Usage: join-chatroom <chatroom_name>"

def join_chatroom(sv: SharedVariables):
    # check syntax
    if sv.argc < 2:
        raise RuntimeError(802705, syntax)
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(883041, "Please login first.")
    # check if chatroom exists and is open
    sv.sqlite_cursor.execute("SELECT host,port,status FROM chatrooms WHERE name = ? ", [sv.argv[1]])
    chatroom_info = sv.sqlite_cursor.fetchone()
    if chatroom_info is not None and chatroom_info[2] == 'open':
        sv.tcp_conn.send(MSG_Encode(0, json.dumps(chatroom_info[0:2])))
    else:
        raise RuntimeError(603360, "The chatroom does not exist or the chatroom is closed.")
