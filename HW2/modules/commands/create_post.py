from modules.SharedVariables import SharedVariables
from modules.utility import *

# usage: create-post <board-name> --title <title> --content <content>
def create_post(sv: SharedVariables):
    board_name = sv.argv[1]
    try:
        if sv.argc < 6:
            # too few arguments
            raise RuntimeError(144704, "Usage: create-post <board-name> --title <title> --content <content>")

        title_start = sv.argv.index('--title')
        content_start = sv.argv.index('--content')
        if title_start > content_start:
            # wrong argument order
            raise RuntimeError(144704, "Usage: create-post <board-name> --title <title> --content <content>")

        if sv.session_id == -1:
            raise RuntimeError(251152, "Please login first.")

        if not BoardExists(board_name):
            raise RuntimeError(617845, "Board does not exist.")

        title = " ".join(sv.argv[title_start + 1:content_start])
        content = " ".join(sv.argv[content_start + 1:]).replace("<br>", "\n")

        print(board_name, title, content, sv.username)
        sv.sqlite_cursor.execute("INSERT INTO posts (board, title, content, author) VALUES (?,?,?,?) ", [board_name, title, content, sv.username])
        sv.tcp_conn.send(MSG_Encode(0, "Create post successfully."))
        DebugDB('posts')
        print("create-post success")

    except ValueError:
        errmsg = "--title or --content not found"
        ExceptionInfo(errmsg)
        sv.tcp_conn.send(MSG_Encode(248807, errmsg))
        return

    # deprecated  # (board, title) = (sv.argv[1], sv.argv[3])  # n = 4  # while n < sv.argc and sv.argv[n] != "--content":  #     title = f"{title}
    # {sv.argv[n]}"  #     n = n + 1  # n = n + 1  # content = ""  # while n < sv.argc:  #     content = f"{content} {sv.argv[n]}"  #     n = n + 1
