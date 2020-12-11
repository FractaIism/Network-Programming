#!/usr/bin/env python3

from modules.SharedVariables import SharedVariables
from modules.utility import ExceptionInfo, DoCMD
import modules.chatroom.chatroom_server as chatroom_server
import modules.chatroom.chatroom_client as chatroom_client
from params import *
import socket, json

def main():
    sv = SharedVariables()
    sv.session_id = -1
    sv.username = None
    sv.tcp_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sv.tcp_conn.connect((remoteHost, remotePort))
    sv.udp_conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sv.addr = (remoteHost, remotePort)
    (localHost, localPort) = sv.tcp_conn.getsockname()  # client machine hostname and port, not localhost!
    sv.udp_conn.bind((localHost, localPort))

    # print(f"Connected to server at {remoteHost}:{remotePort}")
    print("********************************")
    print("** Welcome to the BBS server. **")
    print("********************************")

    try:
        last_msg = None
        while True:
            if last_msg is None:
                input_str = input('% ')
            else:
                input_str = last_msg  # when returning from chatroom client
                last_msg = None
            # check for empty command
            argv = input_str.split()
            argc = len(argv)
            if argc == 0:
                continue
            command = argv[0]

            if command == 'create-chatroom':
                (retcode, message) = DoCMD(sv, input_str + ' ' + localHost, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    print("Start to create chatroom …")
                    sv.chatroom_port = int(argv[1])
                    chatroom_server.chatroom_server(sv.username, sv.chatroom_port)
                    chatroom_server.input_thread.join()
                    print("Welcome back to BBS.")
                    if chatroom_server.status == 'leave':
                        DoCMD(sv, "close-chatroom", "TCP")

            elif command == 'list-chatroom':
                (retcode, message) = DoCMD(sv, input_str, "UDP")
                print("{:<15} {:<15}".format("Chatroom_name", "Status"))
                if retcode != 0:
                    print(message)
                else:
                    for name, status in json.loads(message):
                        print("{:<15} {:<15}".format(name, status))

            elif command == 'join-chatroom':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    addr = tuple(json.loads(message))
                    chatroom_client.chatroom_client(sv.username, addr)
                    chatroom_client.input_thread.join()
                    last_msg = chatroom_client.last_msg

            elif command == 'attach':
                if sv.session_id == -1:
                    print("Please login first.")
                elif not chatroom_server.server_online:
                    print("Please create-chatroom first.")
                else:
                    chatroom_server.attach()
                    chatroom_server.input_thread.join()
                    print("Welcome back to BBS.")
                    if chatroom_server.status == 'leave':
                        DoCMD(sv, "close-chatroom", "TCP")

            elif command == 'restart-chatroom':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    print("Start to create chatroom …")
                    sv.chatroom_port = int(message)
                    chatroom_server.chatroom_server(sv.username, sv.chatroom_port)
                    chatroom_server.input_thread.join()
                    print("Welcome back to BBS.")
                    if chatroom_server.status == 'leave':
                        DoCMD(sv, "close-chatroom", "TCP")

            elif command == 'register':
                (retcode, message) = DoCMD(sv, input_str, "UDP")
                print(message)

            elif command == 'whoami':
                if argc != 1:
                    print("Usage: whoami")
                elif sv.session_id == -1:
                    print("Please login first.")
                else:
                    print(sv.username)

            elif command == 'login':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    (sv.session_id, sv.username) = json.loads(message)
                    print(f"Welcome, {sv.username}.")

            elif command == 'logout':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    print(f"Bye, {sv.username}.")
                    sv.session_id = -1
                    sv.username = None

            elif command == 'list-user':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                user_list = json.loads(message)
                print("{:<15} {:<15}".format("Username", "Email"))
                for user in user_list:
                    print("{:<15} {:<15}".format(user[0], user[1]))

            elif command == 'create-board':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)

            elif command == 'list-board':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                boards = json.loads(message)
                print("{:<6} {:<15} {}".format("Index", "Name", "Moderator"))
                for board in boards:
                    print("{:<6} {:<15} {}".format(*board))  # spread operator

            elif command == 'create-post':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)

            elif command == 'update-post':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)

            elif command == 'delete-post':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)

            elif command == 'list-post':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    formatSpec = "{:<5} {:<20} {:<15} {}"
                    print(formatSpec.format("S/N", "Title", "Author", "Date"))
                    for post in json.loads(message):
                        print(formatSpec.format(*post))

            elif command == 'comment':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)  # success or error message

            elif command == 'read':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                if retcode != 0:
                    print(message)
                else:
                    post_json = json.loads(message)
                    post_info = post_json[0]
                    print("Author: {}\nTitle: {}\nDate: {}\n--\n{}\n--".format(*post_info))
                    comments = post_json[1:]
                    for comment in comments:
                        print("{}: {}".format(*comment))

            elif command == 'exit':
                sv.tcp_conn.send(input_str.encode())
                sv.tcp_conn.close()
                sv.udp_conn.close()
                exit()

            elif command == 'help':
                (retcode, message) = DoCMD(sv, input_str, "TCP")
                print(message)

            else:  # unknown command
                print(f"Unknown command '{command}'. Type 'help' for a list of commands.")

    except ConnectionError:
        ExceptionInfo()
    sv.tcp_conn.close()
    exit()

# except Exception as e:
#     ExceptionInfo()
pass

if __name__ == '__main__':
    main()
