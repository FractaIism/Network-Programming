from modules.utility import *

# Usage: list-user
def list_user(sv: SharedVariables):
    records = sv.sqlite_cursor.execute('SELECT username,email FROM users')
    user_list = []
    for rec in records:
        user_list.append(rec)
    sv.tcp_conn.send(MSG_Encode(0, json.dumps(user_list)))
    # print(user_list)
