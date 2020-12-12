from modules.utility import *

# usage: create-post <board-name> --title <title> --content <content>
def create_post(sv: SharedVariables):
    board_name = sv.argv[1]
    # check syntax
    if sv.argc < 6:
        # too few arguments
        raise RuntimeError(144704, "Usage: create-post <board-name> --title <title> --content <content>")
    try:
        title_start = sv.argv.index('--title')
        content_start = sv.argv.index('--content')
    except ValueError:
        # --title or --content not found
        raise RuntimeError(248807, "Usage: create-post <board-name> --title <title> --content <content>")
    if title_start > content_start:
        # wrong argument order
        raise RuntimeError(144704, "Usage: create-post <board-name> --title <title> --content <content>")
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(251152, "Please login first.")
    # check if board exists
    if not BoardExists(board_name):
        raise RuntimeError(617845, "Board does not exist.")
    # create post
    title = " ".join(sv.argv[title_start + 1:content_start])
    content = " ".join(sv.argv[content_start + 1:]).replace("<br>", "\n")
    # print(board_name, title, content, sv.username)
    sv.sqlite_cursor.execute("INSERT INTO posts (board, title, content, author) VALUES (?,?,?,?) ", [board_name, title, content, sv.username])
    sv.tcp_conn.send(MSG_Encode(0, "Create post successfully."))
    # DebugDB('posts')
