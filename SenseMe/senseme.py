"""
class SenseMeFan:
This class provides TCP/UDP access to Haiku SenseMe capable fans.
Based on work from Bruce at http://bruce.pennypacker.org/tag/senseme-plugin/
https://github.com/bpennypacker/SenseME-Indigo-Plugin

Source can be found at https://github.com/TomFaulkner/SenseMe
"""

import logging
import re
import socket


logging.getLogger(__name__).addHandler(logging.NullHandler())


class SenseMe:
    def __init__(self, ip='', name='', model='', series=''):
        self.PORT = 31415

        if not ip or not name:
            self.discover()
        else:
            self.ip = ip
            self.name = name
            self.mac = ''
            self.details = ''
            self.model = model
            self.series = series

        self.light = {'brightness': None, 'status': None}
        self.fan = {'speed': None, 'status': None}

        # self.getstate()

    def __send_command__(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode('utf-8'))
        sock.close()

    def __query__(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode('utf-8'))

        try:
            status = sock.recv(1048).decode('utf-8')
            print('Status: ' + status)
        except socket.timeout:
            print('Socket Timed Out')
        else:
            sock.close()
            print(str(status))
            match_obj = re.match('\(.*;([^;]+)\)', status)
            if match_obj:
                return match_obj.group(1)
            else:
                return False

    def set_speed(self, speed):
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0
        self.__send_command__('<%s;FAN;SPD;SET;%s>' % (self.name, speed))

    def inc_speed(self, increment=1):
        self.get_fan()
        self.set_speed(int(self.fan['speed']) + increment)
        return

    def dec_speed(self, decrement=1):
        self.get_fan()
        self.set_speed(int(self.fan['speed']) - decrement)
        return

    def set_light(self, light):
        if light > 16:  # max light level, if receiving > 16 fan auto changes to 16
            light = 16
        elif light < 0:  # light 0 also automatically sets pwr = off
            light = 0
        self.__send_command__('<%s;LIGHT;LEVEL;SET;%s>' % (self.name, light))

    def inc_light(self, increment=1):
        self.get_light()
        self.set_light(int(self.light['brightness']) + increment)
        return

    def dec_light(self, decrement=1):
        self.get_light()
        self.set_light(int(self.light['brightness']) - decrement)
        return

    def fan_off(self):
        self.__send_command__('<%s;FAN;PWR;OFF>' % self.name)

    def fan_on(self):
        self.__send_command__('<%s;FAN;PWR;ON>' % self.name)

    def fan_toggle(self):
        self.get_fan()
        if self.fan['status'] == 'ON':
            self.fan_off()
            return 'OFF'
        else:
            self.fan_on()
            return 'ON'

    def light_off(self):
            self.__send_command__('<%s;LIGHT;PWR;OFF>' % self.name)

    def light_on(self):
        self.__send_command__('<%s;LIGHT;PWR;ON>' % self.name)

    def light_toggle(self):
        self.get_light()
        if self.light['status'] == 'ON':
            self.light_off()
            return 'OFF'
        else:
            self.light_on()
            return 'ON'

    def get_light(self):
        self.light['brightness'] = self.__query__('<%s;LIGHT;LEVEL;GET;ACTUAL>' % self.name)
        self.light['status'] = self.__query__('<%s;LIGHT;PWR;GET>' % self.name)
        return self.light

    def get_fan(self):
        self.fan['speed'] = self.__query__('<%s;FAN;SPD;GET;ACTUAL>' % self.name)
        self.fan['status'] = self.__query__('<%s;FAN;PWR;GET>' % self.name)

    def __get_state__(self):
        self.get_fan()
        self.get_light()

    @property
    def fan_speed(self):
        return self.get_fan()

    @property
    def light_level(self):
        return self.get_light()

    @staticmethod
    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 31415))
        for x in range(1, 30):
            m = sock.recvfrom(1024)
            print(m)

    def discover(self):
        data = '<ALL;DEVICE;ID;GET>'.encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        logging.debug("Sending broadcast.")
        s.sendto(data, ('<broadcast>', self.PORT))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.debug("Listening...")
        try:
            s.bind(('', self.PORT))
            m = s.recvfrom(1024)
            print(m)
            if not m:
                print('not m')
                pass
            else:
                self.details = m[0].decode('utf-8')
                res = re.match('\((.*);DEVICE;ID;(.*);(.*),(.*)\)', self.details)
                self.name = res.group(1)
                self.mac = res.group(2)
                self.model = res.group(3)
                self.series = res.group(4)
                self.ip = m[1][0]
                print(self.name, self.mac, self.model, self.series)
        except OSError as e:
            # Address already in use
            logging.critical("Port is in use or could not be opened. Is another instance running?\n%s" % e)
            raise OSError
