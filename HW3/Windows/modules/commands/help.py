from modules.utility import *
import inspect

def command_list(sv: SharedVariables):
    sv.tcp_conn.send(MSG_Encode(0, inspect.cleandoc('''
        Command list:
        register <username> <email> <password>
        login <username> <password>
        logout
        whoami
        list-user
        create-board <name>
        create-post <board-name> --title <title> --content <content>
        list-board
        list-post <board-name>
        read <post-S/N>
        delete-post <post-S/N>
        update-post <post-S/N> --title/content <new>
        comment <post-S/N> <comment>
        create-chatroom <port>
        list-chatroom
        join-chatroom <chatroom_name>
        attach
        restart-chatroom
        exit
    ''')))
