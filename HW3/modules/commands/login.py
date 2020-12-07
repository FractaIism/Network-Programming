from modules.utility import *
from random import randint

# Usage: login <username> <password>
def login(sv: SharedVariables):
    (input_username, input_password) = sv.argv[1:3]
    # check syntax
    if sv.argc != 3:
        raise RuntimeError(747617, "Usage: login <username> <password>")
    # check login status
    if sv.session_id != -1:
        raise RuntimeError(336368, "Please logout first.")
    # check if user exists
    sv.sqlite_cursor.execute('SELECT username,password FROM users WHERE username = ?', [input_username])
    credentials = sv.sqlite_cursor.fetchone()
    if credentials is None:
        raise RuntimeError(374245, "Login failed.")
    # check if password matches
    if credentials[1] != input_password:
        raise RuntimeError(449241, "Login failed.")
    # login success
    sv.session_id = randint(1, 9223372036854775807)
    sv.username = credentials[0]
    sv.sqlite_cursor.execute("INSERT INTO sessions (session_id,username) VALUES (?,?) ", [sv.session_id, sv.username])
    sv.tcp_conn.send(MSG_Encode(0, json.dumps([sv.session_id, sv.username])))
