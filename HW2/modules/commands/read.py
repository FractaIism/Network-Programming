from modules.utility import *

# Usage: read <post-S/N>
def read(sv: SharedVariables):
    # check syntax
    if sv.argc != 2:
        raise RuntimeError(845352, "Usage: read <post-S/N>")
    # check if post exists
    post_sn = sv.argv[1]
    if not PostExists(post_sn):
        raise RuntimeError(50913, "Post does not exist.")
    # read post
    post_info = sv.sqlite_cursor.execute("SELECT author, title, date, content FROM posts WHERE serial_number = ? ", [post_sn]).fetchone()
    # change date format
    _post_info = list(post_info)
    _post_info[2] = ShortDate(_post_info[2])
    post = [tuple(_post_info)]
    comments = sv.sqlite_cursor.execute("SELECT author, content FROM comments WHERE post_sn = ? ORDER BY idx", [post_sn])
    for comment in comments.fetchall():
        post.append(comment)
    sv.tcp_conn.send(MSG_Encode(0, json.dumps(post)))
