import socket, json, sys

try:
    print(sys.argv)
    print(len(sys.argv))
    print(sys.argv[0])
    print(123 if sys.argv[1] is not None else 432)
except Exception as e:
    print("Exception: ", e)
