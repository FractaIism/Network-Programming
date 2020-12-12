from modules.utility import *

# Usage: register <username> <email> <password>
def register(sv: SharedVariables):
    # check syntax
    if sv.argc != 4:
        raise RuntimeError(306915, "Usage: register <username> <email> <password>")
    # check for duplicate username
    sv.sqlite_cursor.execute('SELECT username FROM users WHERE username = ?', [sv.argv[1]])
    if sv.sqlite_cursor.fetchone() is not None:
        raise RuntimeError(27387, "Username is already used.")
    # add user to database
    sv.sqlite_cursor.execute("INSERT INTO users ('username','email','password') VALUES (?,?,?)", sv.argv[1:4])
    sv.udp_conn.send(MSG_Encode(0, "Register successfully."))
