from modules.SharedVariables import SharedVariables
from modules.utility import *

# Usage: whoami
# Receive: whoami <session-id>
# deprecated. handle on client side
def whoami(sv: SharedVariables):
    # check syntax
    if sv.argc != 2:
        raise RuntimeError(955327, "Usage: whoami")
    # check login status
    if sv.session_id == -1:
        raise RuntimeError(923881, "Please login first.")
    # return username
    sv.udp_conn.send(MSG_Encode(0, sv.username))
