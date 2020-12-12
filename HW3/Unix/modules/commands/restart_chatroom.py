from modules.utility import *

syntax = "Usage: restart-chatroom"

def restart_chatroom(sv: SharedVariables):
    # check syntax
    if sv.argc > 1:
        raise RuntimeError(686145, syntax)
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(24283, "Please login first.")
    # check chatroom status
    chatroom_status = sv.sqlite_cursor.execute("SELECT status,port FROM chatrooms WHERE name = ? ", [sv.username]).fetchone()
    if chatroom_status is None:
        raise RuntimeError(931619, "Please create-chatroom first.")
    if chatroom_status[0] == 'open':
        raise RuntimeError(210644, "Your chatroom is still running.")
    chatroom_port = chatroom_status[1]
    sv.tcp_conn.send(MSG_Encode(0, chatroom_port))
    sv.sqlite_cursor.execute("UPDATE chatrooms SET status = 'open' WHERE name = ? ", [sv.username])
