from modules.utility import *

# Usage: delete-post <post-S/N>
def delete_post(sv: SharedVariables):
    # check syntax
    if sv.argc != 2:
        raise RuntimeError(852327, "Usage: delete-post <post-S/N>")
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(187769, "Please login first.")
    # check if post exists
    post_sn = sv.argv[1]
    if not PostExists(post_sn):
        raise RuntimeError(449229, "Post does not exist.")
    # check permissions
    author = sv.sqlite_cursor.execute("SELECT author FROM posts WHERE serial_number = ? ", [post_sn]).fetchone()[0]
    if sv.username != author:
        raise RuntimeError(624428, "Not the post owner.")
    # delete post
    sv.sqlite_cursor.execute("DELETE FROM posts WHERE serial_number = ? ", [post_sn])
    sv.tcp_conn.send(MSG_Encode(0, "Delete post successfully."))
    # DebugDB('posts')
