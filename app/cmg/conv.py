# -*- coding: utf-8 -*-

import json

from hashlib import sha256


def hash(data):
    '''Short function for creating hash sha256.'''
    return sha256(str(data).encode()).hexdigest()


def hash_color(data):
    '''Return list of colors in HEX format. It use hash() function to create
    string which length of 64 characters. Then it takes substring of 60
    characters and divides into 10 parts. Each part is color.

    '''
    return ['#{}'.format(hash(data)[2:-2][c:c + 6])
            for c in range(0, len(hash(data)[2:-2]), 6)]


def flot_chart(xl, yl, sx=2400, sy=-102, ex=2480, ey=-102):
    '''Return list of chart points such [[x0, y0], [x1, y2], ... [xN, yN]]
    for Flot library (JavaScript). Arguments sx, sy, ex, ey use for
    supporting different types of modules.

    Keyword arguments:
    xl -- list of x coordinates
    yl -- list of y coordinates
    sx -- first x coordinate
    sy -- first y coordinate
    ex -- last x coordinate
    ey -- last y coordinate

    '''
    if len(xl) == len(yl):
        return ([[sx, sy], [xl[0], sy]]
                + [[xl[i], int(yl[i])] for i in range(len(xl))]
                + [[xl[-1], ey], [ex, ey]])


def time(ms):
    '''Return time's string from milliseconds to view
    days/hours:minutes:seconds.

    '''
    r = ''
    s = (ms // 1000) % 60
    m = (ms // 60000) % 60
    h = (ms // 3600000) % 24
    d = (ms // 86400000)

    if d:
        r = ''.join([r, str(d), '/'])

    if h:
        if d:
            h = '%02d' % h
        r = ''.join([r, str(h), ':'])

    if m:
        if h:
            m = '%02d' % m
        r = ''.join([r, str(m), ':'])

    s = '%02d' % s if m else s

    return ''.join([r, str(s)])


def to_json(dict_, type_=None):
    if type_ == 'm' or type_ is None:
        if type_ is None:
            return json.dumps(dict_, ensure_ascii=True, indent=4,
                              sort_keys=True)
        else:
            return json.dumps(dict_).replace(' ', '')


def from_json(json_):
    return json.loads(json_)