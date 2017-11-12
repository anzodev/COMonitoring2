# -*- coding: utf-8 -*-

import threading
import logging
import time
import sys
import sock
import conv

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


def gethost(host_c, pc_cn, ps_cn, key, attempt=3, interval=1):
    '''Return server's IP address.'''
    s = sock.TCP(host_c, pc_cn, listen=1, timeout=interval)
    count  = 0
    host   = None

    while count < attempt:
        sock.send(
            type_='udp',
            host='255.255.255.255',
            port=ps_cn,
            data='connection',
            broadcast=True
        )
        data = s.recv()
        if not data is None:
            pckg = conv.from_json(data)
            if pckg['k'] == key:
                host = pckg['h']
                break
        count += 1

    s.close()
    return host



class Server(threading.Thread):

    def __init__(self, host, ps_w, ps_cn, ps_tc, ps_tm, pc_cn,
                 pc_tc, pc_at, key, i_server, root):
        threading.Thread.__init__(self)
        self.host     = host
        self.ps_w     = ps_w
        self.ps_cn    = ps_cn
        self.ps_tc    = ps_tc
        self.ps_tm    = ps_tm
        self.pc_cn    = pc_cn
        self.pc_tc    = pc_tc
        self.pc_at    = pc_at
        self.key      = key

        self.app      = Flask(__name__, root_path=root)
        self.socketio = SocketIO(self.app)
        self.clients  = []
        if i_server: self.clients.append(self.host)

        logging.basicConfig(level=logging.ERROR)

    def __connector(self):
        s = sock.UDP('0.0.0.0', self.ps_cn, broadcast=True)
        while True:
            data = s.recv()
            if data[0] == 'connection':
                self.clients.append(data[1])
                pckg = conv.to_json({
                    'h': self.host,
                    'k': self.key
                }, 'm')
                sock.send('tcp', data[1], self.pc_cn, pckg)

    def __transfer_clients(self):
        time.sleep(2)
        s = sock.TCP(self.host, self.ps_tc, timeout=1)
        while True:
            result       = []
            to_render    = []
            to_refresh   = {'a': 'set_clients', 'd': []}

            for addr in self.clients:
                if sock.send('tcp', addr, self.pc_tc, 1):
                    data = s.recv()
                    if not data is None:
                        pckg = conv.from_json(data)
                        if pckg['k'] == self.key:
                            del pckg['k']
                            result.append(addr)
                            to_render.append(pckg)
                            to_refresh['d'].append(pckg['h'])

            if result != self.clients:
                self.clients = result
                sock.send('tcp', addr, self.pc_at, to_refresh)

            self.socketio.emit('render_clients', {'data': to_render})
            time.sleep(2)

    def __transfer_modules(self):
        s = sock.TCP(self.host, self.ps_tm)
        while True:
            data = s.recv()
            try:
                pckg = conv.from_json(data)
            except json.decoder.JSONDecodeError:
                pass
            else:
                if pckg['k'] == self.key:
                    del pckg['k']
                    self.socketio.emit('render_modules', {'data': pckg})
            finally:
                pass

    def run(self):
        @self.app.route('/')
        def index():
            return render_template('app.html')

        @self.socketio.on('set_name')
        def set_name(data):
            pckg = conv.to_json({
                'a': 'set_name',
                'd': data[1]
            }, 'm')
            sock.send('tcp', data[0], self.pc_at, pckg)

        @self.socketio.on('set_color')
        def set_color(data):
            pckg = conv.to_json({
                'a': 'set_color',
                'd': data[1],
            }, 'm')
            sock.send('tcp', data[0], self.pc_at, pckg)

        @self.socketio.on('set_chart_type')
        def set_chart_type(data):
            pckg = conv.to_json({
                'a': 'set_chart_type',
                'd': data[1]
            }, 'm')
            sock.send('tcp', data[0], self.pc_at, pckg)

        self.socketio.start_background_task(target=self.__connector)
        self.socketio.start_background_task(target=self.__transfer_clients)
        self.socketio.start_background_task(target=self.__transfer_modules)
        self.socketio.run(self.app, self.host, self.ps_w)
