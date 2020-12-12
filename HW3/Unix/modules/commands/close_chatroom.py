from modules.utility import *

# this is an system command, not meant to be called from the client command line
def close_chatroom(sv: SharedVariables):
    sv.sqlite_cursor.execute("UPDATE chatrooms SET status = 'closed' WHERE name = ? ", [sv.username])
    sv.tcp_conn.send(MSG_Encode(0))
