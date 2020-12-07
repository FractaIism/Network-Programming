from modules.utility import *

# Usage: logout
def logout(sv: SharedVariables):
    # check syntax
    if sv.argc != 1:
        raise RuntimeError(26635, "Usage: logout")
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(552072, "Please login first.")
    # logout
    sv.sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [sv.session_id])
    sv.tcp_conn.send(MSG_Encode(0))
    sv.session_id = -1
    sv.username = None
