from modules.utility import *

# Usage: list-post <board-name>
def list_post(sv: SharedVariables):
    # check syntax
    if sv.argc != 2:
        raise RuntimeError(621441, "Usage: list-post <board-name>")
    # check if board exists
    board_name = sv.argv[1]
    if not BoardExists(board_name):
        raise RuntimeError(549042, "Board does not exist.")
    # fetch posts
    posts = sv.sqlite_cursor.execute("SELECT serial_number, title, author, date FROM posts WHERE board = ? ", [board_name]).fetchall()
    # change date format
    for index, post in enumerate(posts):
        _post = list(post)
        _post[3] = ShortDate(_post[3])
        posts[index] = tuple(_post)
    sv.tcp_conn.send(MSG_Encode(0, json.dumps(posts)))
    # print(posts)
