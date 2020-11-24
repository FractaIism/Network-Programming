import sys,os

# common
argv = sys.argv
argc = len(argv)
bufsize = 4096

# server-side
if os.path.basename(argv[0]) == 'server.py':
    host = ''  # bind to this machine
    port = 9746 if argc < 2 else int(sys.argv[1])
    sqlite_db = 'file:nphw2?mode=memory&cache=shared'

# client-side
if os.path.basename(argv[0]) == 'client.py':
    remoteHost = 'localhost' if argc < 2 else sys.argv[1]
    remotePort = 9746 if argc < 3 else int(sys.argv[2])
