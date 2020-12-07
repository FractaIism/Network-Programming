from modules.utility import *

# Usage: create-board <name>
def create_board(sv: SharedVariables):
    # check syntax
    if sv.argc != 2:
        raise RuntimeError(196657, "Usage: create-board <name>")
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(730253, "Please login first.")
    # check if board exists
    board_name = sv.argv[1]
    if BoardExists(board_name):
        raise RuntimeError(57238, "Board already exists.")
    # create board
    sv.sqlite_cursor.execute("INSERT INTO boards (name, moderator) VALUES (?,?) ", [board_name, sv.username])
    sv.tcp_conn.send(MSG_Encode(0, "Create board successfully."))
