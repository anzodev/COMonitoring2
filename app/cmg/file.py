# -*- coding: utf-8 -*-

from datetime import datetime


def unique_name(name=None):
    '''Return unique string for file's naming.'''
    unique_string = str(datetime.now()).split('.')[0].replace(' ', '_')
    if not name is None:
        return '_'.join([str(name), unique_string])
    else:
        return unique_string


def format(name):
    '''Get file's format.'''
    return name[name.rfind('.') + 1:] if '.' in name else None


def read(path):
    '''Short function for reading data from the file.'''
    data = None
    with open(path, encoding='utf-8') as f:
        data = f.read()
        f.close()
    return data


def write(path, data, method):
    '''Short function for writing data into the file.'''
    with open(str(path), method) as f:
        f.write(str(data))
        f.close()
    return True

