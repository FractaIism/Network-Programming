from modules.utility import *

syntax = "Usage: list-chatroom"

def list_chatroom(sv: SharedVariables):
    if sv.argc > 1:
        raise RuntimeError(997601, syntax)
    if sv.session_id == -1:
        raise RuntimeError(501758, "Please login first.")
    sv.sqlite_cursor.execute("SELECT name,status FROM chatrooms")
    chatrooms = sv.sqlite_cursor.fetchall()
    print(chatrooms)
    sv.udp_conn.send(MSG_Encode(0, json.dumps(chatrooms)))
