import pickle
import socket

from exceptions import Continue


def send_message(s: socket.socket, request: dict):
    s.sendall(pickle.dumps(request))
    response = pickle.loads(s.recv(4096))

    if 'error' in response:
        raise Continue()

    return response