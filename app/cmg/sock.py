# -*- coding: utf-8 -*-

import socket


class TCP:

    def __init__(self, host, port, listen=5, buff=4096, timeout=None):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if not timeout is None:
            self.s.settimeout(timeout)
        self.s.bind((host, port))
        self.s.listen(listen)
        self.buff = buff

    def recv(self):
        data = ''
        try:
            conn = self.s.accept()[0]
        except socket.timeout:
            data = None
        else:
            while True:
                part = conn.recv(self.buff).decode()
                if len(part) != 0:
                    data = ''.join([data, part])
                else:
                    break
            conn.close()
        return data

    def accept_close(self):
        self.s.accept()[0].close()

    def close(self):
        self.s.close()


class UDP:

    def __init__(self, host, port, buff=4096, broadcast=True):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if broadcast:
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((host, port))
        self.buff = buff

    def recv(self):
        pckg = self.s.recvfrom(self.buff)
        return (pckg[0].decode(), pckg[1][0])

    def close(self):
        self.s.close()


def try_conn(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
        except ConnectionRefusedError:
            return False
        else:
            return True
        finally:
            s.close()


def send(type_, host, port, data, broadcast=False):
    data = str(data).encode()
    if type_ == 'tcp':
        s_type = socket.SOCK_STREAM
    elif type_ == 'udp':
        s_type = socket.SOCK_DGRAM
    else:
        return

    with socket.socket(socket.AF_INET, s_type) as s:
        if type_ == 'tcp':
            try:
                s.connect((host, port))
            except ConnectionRefusedError:
                return False
            else:
                s.sendall(data)
                return True
            finally:
                s.close()
        elif type_ == 'udp':
            if broadcast:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(data, (host, port))
            s.close()
        else:
            return
