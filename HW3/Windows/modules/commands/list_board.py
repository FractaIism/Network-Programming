from modules.utility import *

# Usage: list-board
def list_board(sv: SharedVariables):
    records = sv.sqlite_cursor.execute("SELECT * FROM boards")
    sv.tcp_conn.send(MSG_Encode(0, json.dumps(list(records))))
