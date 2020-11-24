from modules.SharedVariables import SharedVariables
from modules.utility import *

# Usage: update-post <post-S/N> --title/content <new>
def update_post(sv: SharedVariables):
    if sv.argc < 4:
        raise RuntimeError(852327, "Usage: update-post <post-S/N> --title/content <new>")
    if sv.session_id == -1:
        raise RuntimeError(187769, "Please login first.")
    post_sn = sv.argv[1]
    if not PostExists(post_sn):
        raise RuntimeError(449229, "Post does not exist.")
    author = sv.sqlite_cursor.execute("SELECT author FROM posts WHERE serial_number = ? ", [post_sn]).fetchone()[0]
    if sv.username != author:
        raise RuntimeError(624428, "Not the post owner.")

    if sv.argv[2] == '--title':
        field = 'title'
    elif sv.argv[2] == '--content':
        field = 'content'
    else:
        raise Exception("Invalid field")
    newdata = " ".join(sv.argv[3:]).replace("<br>", "\n")
    sv.sqlite_cursor.execute(f"UPDATE posts SET {field} = ? WHERE serial_number = ? ", [newdata, post_sn])
    sv.tcp_conn.send(MSG_Encode(0, "Update post successfully."))
    print("update-post success")
    DebugDB('posts')
