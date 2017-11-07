# -*- coding: utf-8 -*-

import os
import conv
import machine


def parse(dict_):

    s = '  COMonitoring2\n\n'
    s = ''.join([s, '\n  %-16s%s' % ('server address', dict_['s_addr'])])

    s = ''.join([s, '\n  %-16s%s' % ('system nodes', '[')])
    if len(dict_['sys_nodes']) != 0:
        for n in dict_['sys_nodes']:
            s = ''.join([s, '\n  %-16s    %s' % ('', n)])
        s = ''.join([s, '\n  %-16s%s' % ('', ']')])
    else:
        s = ''.join([s, ']'])

    s = ''.join([s, '\n\n  %-16s%s' % ('host', dict_['h'])])
    s = ''.join([s, '\n  %-16s%s' % ('name', dict_['n'])])
    s = ''.join([s, '\n  %-16s%s' % ('os', dict_['os'])])

    s = ''.join([s, '\n\n  %-16s%s' % ('modules', '[')])
    if len(dict_['m']) != 0:
        for key, value in dict_['m'].items():
            s = ''.join(
                [
                    s,
                    '\n  %-16s    %s  %s  %3s (%s)' % (
                        '', key, value['color'], value['chart_type'],
                        value['status']
                    )
                ]
            )
        s = ''.join([s, '\n  %-16s%s' % ('', ']')])
    else:
        s = ''.join([s, ']'])

    return s


def out(data):
    if machine.platform.startswith('linux'):
        os.system('clear')
    else:
        os.system('cls')
    print(data)