# -*- coding: utf-8 -*-

import threading
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], 'cmg/'))

from cmg import conv
from cmg import file
from cmg import module
from cmg import machine
from cmg import sock
from cmg import serv
from cmg import output
from time import sleep

#sudo usermod -a -G dialout $USER

ROOT = sys.path[0]
PATH_CONFIG = os.path.join(ROOT, 'config')


def transfer_client(host, port):
    '''Process that sends data about current client.'''
    global host_s
    global conf
    global os_name
    global modules_qty
    global key

    s = sock.TCP(host, port)
    while True:
        data = s.recv()
        # print(data)
        if int(data):
            pckg = conv.to_json({
                'h': host,         # client's IP adderss
                'n': conf['NAME'], # client's name
                'os': os_name,     # client's operating system name
                'q': modules_qty,  # quantity of connected client's modules
                'k': key           # secret key for integrity confirm
            }, 'm')
            sock.send('tcp', host_s, ps_tc, pckg)


def accept_task(host, port):
    '''Process that accpets tasks from server and puts it into task_queue.
    Task view: {'a': <action>, 'd': <data>}

    <action>         | <data>

    'set_color'      | [serial name (str), color index (int)]
    'set_chart_type' | [serial name (str), chart type (int)]
    'set_name'       | name(str)
    'set_clients'    | [IP addresses of all connected clients(str)]

    '''
    global task_queue

    s = sock.TCP(host, port)
    while True:
        data = s.recv()
        task_queue.append(conv.from_json(data))


if __name__ == '__main__':

    host         = machine.gethost()
    os_name      = machine.name()

    conf         = conv.from_json(file.read(PATH_CONFIG))
    conf['NAME'] = os_name if conf['NAME'] == '' else conf['NAME']

    key          = conv.hash(conf['SECRET_KEY'])
    pc_cn        = conf['PC_CN'] # client's port for connector() method
    pc_tc        = conf['PC_TC'] # client's port for transfer_clients() method
    pc_at        = conf['PC_AT'] # client's port for accept_task() function
    ps_cn        = conf['PS_CN'] # server's port for connector() method
    ps_tc        = conf['PS_TC'] # server's port for transfer_clients() method
    ps_tm        = conf['PS_TM'] # server's port for transfer_modules() method
    ps_w         = conf['PS_W']  # server's port for working

    modules_qty  = 0  # quantity of connected modules
    modules      = {} # storage for modules objects
    colors       = {} # storage for modules colors
    chart_type   = {} # storage for modules chart types
    task_queue   = [] # storage for tasks
    ports_temp   = [] # temporary storage for COM ports list

    conn_attempt = 0     # quantity of connection attempt to server
    clients      = []    # list of clients IP address
    rebuild      = False # flag for JS script to rebuild HTML structure
    i_server     = True

    host_s = serv.gethost(host, pc_cn, ps_cn, key) # try to get server's host, if not found run server

    if host_s is None:
        host_s   = host
        i_server = True

    if i_server:
        serv.Server(host_s, ps_w, ps_cn, ps_tc, ps_tm, pc_cn,
                    pc_tc, pc_at, key, i_server, ROOT).start()

    info = {
        's_addr': ''.join([host_s, ':', str(ps_w)]),
        'sys_nodes': clients,
        'h': host,
        'n': conf['NAME'],
        'os': os_name,
        'm': {}
    }
    output.out(output.parse(info))

    threading.Thread(target=accept_task, args=(host, pc_at)).start()
    threading.Thread(target=transfer_client, args=(host, pc_tc)).start()

    while True:
        if task_queue != []:
            for task in task_queue:
                if task['a'] == 'set_color':
                    # change module's color index in storage variable (1, ..., 10)
                    colors[conv.from_json(task['d'])['s']][1] = int(conv.from_json(task['d'])['i'])
                    rebuild = True

                    info['m'][conv.from_json(task['d'])['s']]['color'] = (
                        colors[conv.from_json(task['d'])['s']][0][colors[conv.from_json(task['d'])['s']][1]]
                    )
                    output.out(output.parse(info))
                elif task['a'] == 'set_chart_type':
                    # change module's chart type in storage variable (0, 1, 10, 100)
                    chart_type[conv.from_json(task['d'])['s']] = int(conv.from_json(task['d'])['t'])
                    rebuild = True

                    info['m'][conv.from_json(task['d'])['s']]['chart_type'] = int(conv.from_json(task['d'])['t'])
                    output.out(output.parse(info))
                elif task['a'] == 'set_name':
                    if task['d'] != '':
                        conf['NAME'] = task['d']
                    else:
                        conf['NAME'] = os_name
                    # rewrite config dictionary for new name value
                    file.write(PATH_CONFIG, conv.to_json(conf), 'w')
                    conf = conv.from_json(file.read(PATH_CONFIG))

                    info['n'] = conf['NAME']
                    output.out(output.parse(info))
                elif task['a'] == 'set_clients':
                    if clients != task['d']:
                        clients = task['d']

                        info['sys_nodes'] = clients
                        output.out(output.parse(info))
                else:
                    pass
                del task_queue[0]
        else:
            ports = module.find_ports()
            if ports != []:
                if ports != ports_temp:
                    del_ = list(set(ports_temp).difference(ports)) # list of disconnected modules
                    add_ = list(set(ports).difference(ports_temp)) # list of new connected modules
                    if del_ != []:
                        for p in del_:
                            info['m'][modules[p].s]['status'] = 'disconnected'
                            del modules[p]

                        output.out(output.parse(info))
                    if add_ != []:
                        for p in add_:
                            modules[p] = module.Module(p) # create new module's object
                            sn = modules[p].s
                            if not sn in colors:
                                colors[sn] = [conv.hash_color(sn), 0] # add new module's colors to storage
                            if not sn in chart_type:
                                chart_type[sn] = 0 # add new module's chart type to storage

                            info['m'][sn] = {
                                'status': 'connected',
                                'color': colors[sn][0][colors[sn][1]],
                                'chart_type': chart_type[sn]
                            }

                        output.out(output.parse(info))

                    rebuild = True

                data = [[], []]
                for p in ports:
                    module_pckg = modules[p].package(chart_type[modules[p].s]) # try to take module's output package
                    if not module_pckg is None:
                        data[0].append(module_pckg)
                        data[1].append([colors[modules[p].s][0],
                                        colors[modules[p].s][1]])
                    else:
                        pass

                if data != [[], []]:
                    ports_temp = ports
                else: # single module was disconnected during cycle above (module.package())
                    info['m'][list(modules.values())[0].s]['status'] = 'disconnected'
                    output.out(output.parse(info))
                    modules    = {}
                    ports_temp = []

                modules_qty = len(ports_temp) # always check if module was disconnected

                pckg = conv.to_json({
                    'h': host,
                    'd': data, # list of all modules data
                    'q': modules_qty,
                    'k': key,
                    'r': rebuild
                }, 'm') # flag 'm' - minimal, delete all spaces from the JSON string

                rebuild = False

                while True:
                    if sock.send('tcp', host_s, ps_tm, pckg): # try to send package
                        if conn_attempt != 0: conn_attempt = 0
                        break
                    elif conn_attempt == 15: # server's crash handler
                        if host == clients.pop(0):
                            i_server = True
                            host_s   = host
                            serv.Server(host_s, ps_w, ps_cn, ps_tc, ps_tm, pc_cn,
                                        pc_tc, pc_at, key, i_server, ROOT).start()
                            break
                        sleep(3)
                        new_host_s = serv.gethost(host, pc_cn, ps_cn, key)
                        if not new_host_s is None:
                            host_s = new_host_s
                        else:
                            break
                    else:
                        conn_attempt += 1
            else:
                sleep(1) # pause for main "while" loop (100% CPU load if task_queue == [] and ports == [])