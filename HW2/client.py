#!/usr/bin/env python3
from modules.SharedVariables import SharedVariables
from modules.utility import ExceptionInfo, DoCMD
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

    # print(f"Connected to server at {remoteHost}:{remotePort}")
    print("********************************")
    print("** Welcome to the BBS server. **")
    print("********************************")

    try:
        while True:
            input_str = input('% ')
            # check for empty command
            argv = input_str.split()
            argc = len(argv)
            if argc == 0:
                continue
            command = argv[0]

            if command == 'register':
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
                    # print("Author:", post_info[0])
                    # print("Title:", post_info[1])
                    # print("Date:", post_info[2])
                    # print("--")
                    # print(post_info[3])
                    # print("--")
                    print("Author: {}\nTitle: {}\nDate: {}\n--\n{}\n--".format(*post_info))
                    # if len(post_json) > 1:
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
