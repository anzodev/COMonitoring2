# -*- coding: utf-8 -*-

import serial
import machine
import conv

from glob import glob


def output_parse(element, data):
    '''Return certain data from module's output.

    Keyword arguments:
    element -- flag that defines what data return
    data -- module's output data

    '''
    if element == 's':
        return data.split(' ')[0].strip()                              # serial name
    elif element == 'p':
        return data.split(' ')[1][1:-1]                                # quantity of packages
    elif element == 't':
        return int(data.split(' ')[2], 16)                             # work time (ms)
    elif element == 'sgl':
        return data[data.find('[') + 2:data.rfind(']') - 1].split(' ') # list of signal level
    else:
        raise RuntimeError('invalid element value: {}'.format(element))


def find_ports():
    '''Return list of connected COM ports.'''
    if machine.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif machine.platform.startswith('linux') or machine.platform.startswith('cygwin'):
        cmd_devices = ('for f in ls /dev/tty*; do udevadm info -q property $f'
                       ' && printf \'\n\'; done')
        result   = []
        required = ('ID_SERIAL_SHORT', 'ID_VENDOR_ID', 'ID_MODEL_ID', 'DEVNAME')
        devices  = os.popen(cmd_devices).read().split('\n\n')[:-1]
        for dev in devices:
            serialized = {row.split('=')[0]: row.split('=')[1]
                          for row in dev.split('\n')[:-1]}

            values = [serialized.get(key) for key in required]
            if None in values:
                continue

            result.append(values[3])
        return result
    elif machine.platform.startswith('darwin'):
        ports = glob('/dev/tty.*')
    else:
        raise EnvironmentError('unsupported platform...')

    result = []
    for port in ports:
        try:
            serial.Serial(port).close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class SignalCounter:

    def __init__(self, quantity, channels=256):
        self.quantity  = quantity
        self.channels  = channels
        self.iteration = 0
        self.counter   = {i: [0, []] for i in range(self.channels)}

    def add(self, signal):
        for i in range(self.channels):
            self.counter[i][0] += int(signal[i])
            self.counter[i][1].append(int(signal[i]))
            if len(self.counter[i][1]) > self.quantity:
                del self.counter[i][1][0]
        self.iteration += 1

    def calc(self, calc_quantity):
        return [sum(self.counter[i][1][-calc_quantity:]) // calc_quantity
                if len(self.counter[i][1]) >= calc_quantity else
                sum(self.counter[i][1]) // len(self.counter[i][1])
                for i in range(self.channels)]

    def calc_all(self):
        return [self.counter[i][0] // self.iteration
                for i in range(self.channels)]


class Module:

    def __init__(self, port, signal_storage=100):
        self.ser          = serial.Serial()
        self.ser.port     = port
        self.ser.baudrate = 9600
        self.ser.timeout  = 1.0

        self.channel_map  = [round(2403 + (i * 0.2863), 2) for i in range(256)]
        self.avg_count    = SignalCounter(signal_storage)
        self.pr           = 0
        self.s            = output_parse('s', self.output())
        self.p            = (port[port.rfind('/') + 4:] if
                             machine.platform.startswith('linux') else port)

    def output(self):
        try:
            self.ser.open()
        except serial.SerialException:
            pass

        if self.ser.isOpen():
            data = ''
            while len(output_parse('sgl', data)) != 256:
                try:
                    data = self.ser.readline().decode()
                except serial.SerialException:
                    data = None
                    break
            self.ser.close()

            if not data is None:
                self.avg_count.add(output_parse('sgl', data))
                self.pr += 1

            return data

    def extract(self):
        data = self.output()
        if not data is None:
            return (
                output_parse('s', data),
                output_parse('p', data),
                output_parse('t', data),
                output_parse('sgl', data)
            )
        else:
            return None

    def package(self, chart_type):
        ext = self.extract()
        if not ext is None:
            pckg = {
                'p': self.p,
                's': self.s,
                'pr': self.pr,
                'pn': ext[1],
                't': conv.time(ext[2]),
                'ct': chart_type
            }

            if chart_type == 0:
                pckg['c'] = conv.flot_chart(self.channel_map, ext[3])
            elif chart_type == 1:
                pckg['c'] = conv.flot_chart(self.channel_map,
                                            self.avg_count.calc_all())
            else:
                pckg['c'] = conv.flot_chart(self.channel_map,
                                            self.avg_count.calc(chart_type))
            return conv.to_json(pckg, 'm')
        else:
            return None