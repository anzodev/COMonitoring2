# -*- coding: utf-8 -*-

import os
import socket

from platform import uname
from sys import platform


def name():
    '''Return string about operating system info.
    For example: Linux #42~16.04.1-Ubuntu

    '''
    return '{} {}'.format(uname().system, uname().version.split()[0])


def gethost():
    '''Return IP address.'''
    if platform.startswith('linux'):
        with socket.socket(type=socket.SOCK_DGRAM) as s:
            s.connect(('8.8.8.8', 1024))
            return s.getsockname()[0]
    elif platform.startswith('win'):
        host = socket.gethostbyname_ex(socket.gethostname())[2][0]
    else:
        raise RuntimeError('unsupported platform...')
    return host
