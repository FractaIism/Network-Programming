from modules.SharedVariables import SharedVariables
from modules.utility import *

# Usage: comment <post-S/N> <comment>
def comment(sv: SharedVariables):
    if sv.argc < 3:
        raise RuntimeError(706550, "Usage: comment <post-S/N> <comment>")
    if sv.session_id == -1:
        raise RuntimeError(993029, "Please login first.")
    (post_sn, content) = (sv.argv[1], " ".join(sv.argv[2:]))
    if not PostExists(post_sn):
        raise RuntimeError(287553, "Post does not exist.")
    sv.sqlite_cursor.execute("INSERT INTO comments (post_sn, author, content) VALUES (?,?,?) ", [post_sn, sv.username, content])
    sv.tcp_conn.send(MSG_Encode(0, "Comment successfully."))
    print("comment success")
    DebugDB("comments")
