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
import time

logging.getLogger(__name__).addHandler(logging.NullHandler())


class SenseMe:
    PORT = 31415

    def __init__(self, ip='', name='', model='', series='', mac=''):
        """
        Suggested use, if not statically defining devices is to call senseme.discover(), 
        which will return a list of SenseMe objects rather than instantiating directly.
        
        However, if ip or name is known instantiating based on that without the other fields works.
        
        If SenseMe is instantiated without ip or name a discovery will be done and the first device to answer
         the broadcast will be the device represented by this object. Any later answers will be ignored.
          
        :param ip: IP address, if known, is not necessary if name is known or only one device exists in the home
        :param name: Device name, as configured/displayed in HaikuHome app. Is not necessary, if IP is known or
         if this is the only device on the network.
        :param model: Device model number, isn't actually used at this time, but could be used in the future if 
         there is a difference in feature sets
        :param series: See comment on model
        :param mac: Could be used to talk to a device if name and ip aren't known, is not currently used.
        """
        if not ip or not name:
            # if ip or name are unknown, discover the device
            # if one is known but not the other a specific device will discover, if not one device, or none,
            #  will discover
            self.discover_single_device()
        else:
            self.ip = ip
            self.name = name
            self.mac = mac
            self.details = ''
            self.model = model
            self.series = series

    def __repr__(self):
        return str({'name': self.name, 'ip': self.ip, 'mac': self.mac, 'model': self.model, 'series': self.series,
                    'light': self.brightness, 'fan': self.speed})

    def __str__(self):
        return 'senseme Device: {}, Series: {}. Speed: {}. Brightness: {}'.format(self.name, self.series,
                                                                                  self.speed,
                                                                                  self.brightness)

    @property
    def speed(self):
        return int(self._query('<%s;FAN;SPD;GET;ACTUAL>' % self.name))

    @speed.setter
    def speed(self, speed):
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0
        self._send_command('<%s;FAN;SPD;SET;%s>' % (self.name, speed))

    def inc_speed(self, increment=1):
        self.speed += increment

    def dec_speed(self, decrement=1):
        self.speed -= decrement

    @property
    def brightness(self):
        return int(self._query('<%s;LIGHT;LEVEL;GET;ACTUAL>' % self.name))

    @brightness.setter
    def brightness(self, light):
        if light > 16:  # max light level, if receiving > 16 fan auto changes to 16
            light = 16
        elif light < 0:  # light 0 also automatically sets pwr = off
            light = 0
        self._send_command('<%s;LIGHT;LEVEL;SET;%s>' % (self.name, light))

    def inc_brightness(self, increment=1):
        self.brightness += increment

    def dec_brightness(self, decrement=1):
        self.brightness += decrement

    @property
    def fan_powered_on(self):
        if self._query('<%s;FAN;PWR;GET>' % self.name) == 'ON':
            return True
        else:
            return False

    @fan_powered_on.setter
    def fan_powered_on(self, power_on=True):
        if power_on:
            self._send_command('<%s;FAN;PWR;ON>' % self.name)
        else:
            self._send_command('<%s;FAN;PWR;OFF>' % self.name)

    def fan_toggle(self):
        if self.fan_powered_on:
            self.fan_powered_on = False
            return False
        else:
            self.fan_powered_on = True
            return True

    @property
    def whoosh(self):
        return ''

    @whoosh.setter
    def whoosh(self, whoosh_on):
        if whoosh_on:
            self._send_command('<%s;FAN;WHOOSH;ON')
        else:
            self._send_command('<%s;FAN;WHOOSH;OFF')

    @property
    def light_powered_on(self):
        if self._query('<%s;LIGHT;PWR;GET>' % self.name) == 'ON':
            return True
        else:
            return False

    @light_powered_on.setter
    def light_powered_on(self, power_on=True):
        if power_on:
            self._send_command('<%s;LIGHT;PWR;OFF>' % self.name)
        else:
            self._send_command('<%s;LIGHT;PWR;ON>' % self.name)

    def light_toggle(self):
        if self.light_powered_on:
            self.light_powered_on = False
            return False
        else:
            self.light_powered_on = True
            return True

    @staticmethod
    def listen():
        """ Listens for broadcasts and logs them for debugging purposes """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 31415))
        for x in range(1, 30):
            m = sock.recvfrom(1024)
            logging.info(m)

    def discover_single_device(self):
        """ Device discovery
         Called during __init__ if the device name or IP address is missing.

        This function will discover only the first device to respond if both name and IP were not provided
         on instantiation. If there is only one device in the home this will work well.
         Otherwise, use the discover function of the module rather than this one. """
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
        except OSError as e:
            # Address already in use
            logging.critical("Port is in use or could not be opened. Is another instance running?\n%s" % e)
            raise OSError
        else:
            try:
                m = s.recvfrom(1024)
                logging.info(m)
                if not m:
                    logging.error("Didn't receive response.")
                else:
                    self.details = m[0].decode('utf-8')
                    res = re.match('\((.*);DEVICE;ID;(.*);(.*),(.*)\)', self.details)
                    # TODO: Parse this properly rather than regex
                    self.name = res.group(1)
                    self.mac = res.group(2)
                    self.model = res.group(3)
                    self.series = res.group(4)
                    self.ip = m[1][0]
                    logging.info(self.name, self.mac, self.model, self.series)
            except OSError as e:
                logging.critical("No device was found.\n%s" % e)
                raise OSError

    def _send_command(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode('utf-8'))
        sock.close()

    def _query(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode('utf-8'))

        try:
            status = sock.recv(1048).decode('utf-8')
            logging.info('Status: ' + status)
        except socket.timeout:
            logging.error('Socket Timed Out')
        else:
            # TODO: this function shouldn't return data OR False, handle this better
            sock.close()
            logging.info(str(status))
            match_obj = re.match('\(.*;([^;]+)\)', status)
            if match_obj:
                return match_obj.group(1)
            else:
                return False

    def send_raw(self, msg):
        """ Send a raw command. Device name is not included.
        Return list of results.
        Sometimes multiple results come in at between iterations and they end 
        up on the same string
        
        :param msg: command to send 
        :return: list of responses as str
        """
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode('utf-8'))

        messages = []
        timeout_occured = False
        while True:
            try:
                recv = sock.recv(1048).decode('utf-8')
                logging.info('Status: ' + recv)
                messages.append(recv)
            except socket.timeout:
                logging.info('Socket Timed Out')
                # most likely this means no more data, give it one more iter
                if timeout_occured:
                    break
                else:
                    timeout_occured = True
            else:
                logging.info(str(recv))
        sock.close()
        return messages

    def _get_all(self):
        """ TODO: finish function
        This function is not complete, and shouldn't yet be used, but I wanted to get changes up to git tonight
        
        Plan is to return a dict of dicts of dicts... to represent all values in getall, handling some special,
        as they are inconsistent on the format. That is, the data values aren't limited to the last segment.
        
        Example: (Living Room Fan;NW;PARAMS;ACTUAL;192.168.1.50;255.255.255.0;192.168.1.1)

        :return: 
        """
        results = self.send_raw('<%s;GETALL>' % self.name)
        # fix double results
        extra_rows = []
        for result in results:
            if ')(' in result:
                halves = result.split(')(')
                result = result.replace(halves[1], ')')
                extra_rows.append(halves[1])
        results.extend(extra_rows)

        res_dict = {}
        for result in results:
            result = result.replace('(', '').replace(')', '')
            _, category, attribute, values = result.split(';', 3)
            if category not in res_dict:
                res_dict['category'] = {}
            if attribute not in res_dict[category]:
                res_dict[category][attribute] = {}
            if len(values.split(';')) > 1:
                values = {values.split(';')[0]: values.split(';')[1]}
            res_dict[category] = {attribute: values}
        # return res_dict

    @staticmethod
    def _parse_values(line):
        if len(line.rsplit(';', 1)) > 1:
            k, v = line.rsplit(';', 1)
            return k, v


def discover(devices_to_find=None, time_to_wait=None):
    port = 31415
    if not devices_to_find:
        devices_to_find = 3
    if not time_to_wait:
        time_to_wait = 5

    data = '<ALL;DEVICE;ID;GET>'.encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    logging.debug("Sending broadcast.")
    s.sendto(data, ('<broadcast>', port))
    logging.debug("Listening...")
    devices = []
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(('', port))
        s.settimeout(2)
        while True:
            try:
                message = s.recvfrom(1024)
            except OSError:
                # timeout occurred
                message = b''
            if message:
                logging.info("Received a message")
                message_decoded = message[0].decode('utf-8')
                res = re.match('\((.*);DEVICE;ID;(.*);(.*),(.*)\)', message_decoded)
                # TODO: Parse this properly rather than regex
                name = res.group(1)
                mac = res.group(2)
                model = res.group(3)
                series = res.group(4)
                ip = message[1][0]
                devices.append(SenseMe(ip=ip, name=name, model=model, series=series, mac=mac))

            time.sleep(.5)
            if start_time + time_to_wait < time.time() or len(devices) >= devices_to_find:
                logging.info("time_to_wait exceeded or devices_to_find met")
                break
        return devices
    except OSError:
        # couldn't get port
        raise OSError("Couldn't get port 31415")
    finally:
        s.close()
