from modules.utility import *

def client_exit(sv: SharedVariables):
    # use client_exit() instead of exit() to prevent shadowing Python builtin exit() function
    sv.sqlite_cursor.execute("DELETE FROM sessions WHERE session_id = ? ", [sv.session_id])
    sv.sqlite_conn.close()
    sv.tcp_conn.close()
    print(f"User {sv.addr} has exited.")
    exit()  # exit thread, server still running
