import socket, sqlite3
from typing import Tuple

class SharedVariables:
    def __init__(self):
        self.tcp_conn = None  # type: socket.SocketKind.SOCK_STREAM
        self.udp_conn = None  # type:socket.SocketKind.SOCK_DGRAM
        # self.sock_type = None  # type:socket.SocketKind
        self.addr = None  # type:Tuple[str,int]
        self.sqlite_conn = None  # type: sqlite3.Connection
        self.sqlite_cursor = None  # type:sqlite3.Cursor
        self.session_id = None  # type:int
        self.username = None  # type:str
        self.argc = None  # type:int
        self.argv = None  # type:list

# Old, more generic but provides no type hints
# usage: pass SharedVariables object as argument and call
#        locals().update(SharedVars.__dict__) to pass in the shared variables
# class SharedVariables:
#     # a data structure to hold variables to be shared across files/modules
#     def __init__(self, args: dict):
#         # args: dictionary of variable names and values
#         for (varname, value) in args.items():
#             self.__dict__[varname] = value
