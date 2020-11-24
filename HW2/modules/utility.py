import sys, os, inspect, sqlite3, json
from params import *
from modules.SharedVariables import SharedVariables

# print exception info and line number
def ExceptionInfo(message: str = ""):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    funcname = inspect.currentframe().f_back.f_code.co_name
    # print("Exception info: ", exc_type, filename, funcname, exc_tb.tb_lineno,exc_obj)
    print("Exception caught:", exc_type, exc_obj)
    print("Exception at:", filename, funcname, exc_tb.tb_lineno)
    if message != "":
        print("Exception message:", message)

# view database contents
def DebugDB(table = "*"):
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    if table == "*":
        table = ["boards", "posts", "comments"]
    if not isinstance(table, list):
        table = [table]

    print()
    print(f"DebugDB: {table}")
    for tab in table:
        print(f"TABLE {tab}:")
        # get column names
        columns = sqlite_conn.execute(f"PRAGMA table_info({tab})")
        col_names = []
        for col in columns:
            col_names.append(col[1])
        print(col_names)
        # get records
        records = sqlite_conn.execute(f"SELECT * FROM {tab}")
        for rec in records:
            print(rec)
        print()

# data struct to send error message along with return code
def MSG_Encode(retcode: int, message: str = "Default message") -> bytes:
    pkg = {
        'retcode': retcode,
        'message': message
    }
    return json.dumps(pkg).encode()

# inverse of MSG_Encode
def MSG_Decode(bytestream: bytes) -> (int, str):
    msg_str = bytestream.decode()
    msg = json.loads(msg_str)
    return msg['retcode'], msg['message']

def BoardExists(board_name: str) -> bool:
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    match_count = sqlite_conn.execute("SELECT * FROM boards WHERE name = ? ", [board_name]).fetchall()
    return len(match_count) > 0

def PostExists(post_sn: int) -> bool:
    sqlite_conn = sqlite3.connect(sqlite_db, uri = True)
    match_count = sqlite_conn.execute("SELECT * FROM posts WHERE serial_number = ? ", [post_sn]).fetchall()
    return len(match_count) > 0

# send command string to server and return response
def DoCMD(sv: SharedVariables, input_str: str, protocol: str = "TCP") -> (int, str):
    if protocol.upper() == "TCP":
        sv.tcp_conn.send(input_str.encode())
        msg = sv.tcp_conn.recv(bufsize)
        return MSG_Decode(msg)
    elif protocol.upper() == "UDP":
        sv.udp_conn.sendto(input_str.encode(), sv.addr)
        msg = sv.udp_conn.recv(bufsize)
        return MSG_Decode(msg)

# convert datetime string 2020-11-24 07:34:03
# to short form 11/24
# DateTimeLong -> DateTimeShort
def ShortDate(dtl: str):
    dts = f"{dtl[5:7]}/{dtl[8:10]}"
    return dts
