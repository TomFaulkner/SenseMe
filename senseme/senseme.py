"""class SenseMeFan.

This class provides TCP/UDP access to Haiku SenseMe capable fans.
Based on work from Bruce at http://bruce.pennypacker.org/tag/senseme-plugin/
https://github.com/bpennypacker/SenseME-Indigo-Plugin

Source can be found at https://github.com/TomFaulkner/SenseMe
"""
import json
import logging
import re
import socket
import time

from .lib import MWT, BackgroundLoop
from .lib.xml import data_to_xml

LOGGER = logging.getLogger(__name__)

__author__ = 'Tom Faulkner'
__url__ = 'https://github.com/TomFaulkner/SenseMe/'


class SenseMe:
    """SenseMe device class.

    Suggested use, if not statically defining devices is to call
    senseme.discover(), which will return a list of SenseMe objects rather than
    instantiating directly.

    However, if ip or name is known instantiating based on that without the
    other fields works.

    If SenseMe is instantiated without ip or name a discovery will be done and
    the first device to answer the broadcast will be the device represented by
    this object. Any later answers will be ignored.

    After init it is suggested to start_monitoring() to make whoosh and some
    other queries instant rather than blocking for ten or so seconds.
    """

    PORT = 31415

    def __init__(self, ip='', name='', model='', series='', mac='', **kwargs):
        """Init a SenseMe device.

        :param ip: IP address, if known, is not necessary if name is known or
            only one device exists in the home
        :param name: Device name, as configured/displayed in HaikuHome app.
           Is not necessary, if IP is known or if this is the only device on
           the network.
        :param model: Device model number, isn't actually used at this time,
            but could be used in the future if there is a difference in feature
            sets
        :param series: See comment on model
        :param mac: Could be used to talk to a device if name and ip aren't
            known, is not currently used.
        """
        if not ip or not name:
            # if ip or name are unknown, discover the device
            # if one is known but not the other a specific device will discover
            # if not one device, or none, will discover
            self.discover_single_device()
        else:
            self.ip = ip
            self.name = name
            self.mac = mac
            self.details = ''
            self.model = model
            self.series = series
        self.monitor_frequency = kwargs.get('monitor_frequency', 45)
        self._monitoring = False
        self._all_cache = None

        self._background_monitor = BackgroundLoop(self.monitor_frequency,
                                                  self._get_all_bare)
        if kwargs.get('monitor', False):
            self.start_monitor()

    def __repr__(self):
        """Repr Method."""
        return (f"SenseMe(name='{self.name}', ip='{self.ip}', "
                f"model='{self.model}', series='{self.series}', "
                f"mac='{self.mac}')")

    def __str__(self):
        """Str Method."""
        return (f'SenseMe Device: {self.name}, Series: {self.series}. '
                f'(Speed: {self.speed}. Brightness: {self.brightness})')

    @property
    def speed(self):
        """Returns/sets fan speed.

        Valid values are between 0 and 7.
        0 is off, 7 is max.
        """
        # loop and exception handling due to:
        # https://github.com/TomFaulkner/SenseMe/issues/19
        attempts = 0
        while attempts < 2:
            speed = self._query('<%s;FAN;SPD;GET;ACTUAL>' % self.name)
            LOGGER.debug(speed)
            try:
                return int(speed)
            except ValueError:
                attempts += 1
                continue
        return 0

    @speed.setter
    def speed(self, speed):
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0
        self._send_command('<%s;FAN;SPD;SET;%s>' % (self.name, speed))

    def inc_speed(self, increment=1):
        """Increases fan speed by increment value, default is 1."""
        self.speed += increment

    def dec_speed(self, decrement=1):
        """Decreases fan speed by decrement value, default is 1."""
        self.speed -= decrement

    @property
    def brightness(self):
        """Returns/sets light brightness.

        Valid values are between 0 and 16.
        0 is off, 16 is max.
        """
        return int(self._query('<%s;LIGHT;LEVEL;GET;ACTUAL>' % self.name))

    @brightness.setter
    def brightness(self, light):
        if light > 16:
            light = 16
        elif light < 0:
            light = 0
        self._send_command('<%s;LIGHT;LEVEL;SET;%s>' % (self.name, light))

    def inc_brightness(self, increment=1):
        """Increases brighness by increment value, default is 1."""
        self.brightness += increment

    def dec_brightness(self, decrement=1):
        """Decreases fan speed by decrement value, default is 1."""
        self.brightness -= decrement

    @property
    def fan_powered_on(self):
        """Return or sets state of fan power.

        Power On = True
        Power Off = False
        """
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
        """Toggle power state of fan."""
        self.fan_powered_on = not self.fan_powered_on

    @property
    def whoosh(self):
        """Set or retrieve whoosh mode.

        This can have a ten second delay since there is no known one item
        request to retrieve status
        """
        try:
            return self.get_attribute('FAN;WHOOSH;STATUS')
        except KeyError:
            LOGGER.error("FAN;WHOOSH;STATUS wasn't found in dict")
            raise OSError("Fan failed to return whoosh status")

    @whoosh.setter
    def whoosh(self, whoosh_on):
        if whoosh_on:
            self._send_command('<%s;FAN;WHOOSH;ON')
        else:
            self._send_command('<%s;FAN;WHOOSH;OFF')

    @property
    def light_powered_on(self):
        """Return or state of light.

        Power On = True
        Power Off = False
        """
        if self._query('<%s;LIGHT;PWR;GET>' % self.name) == 'ON':
            return True
        return False

    @light_powered_on.setter
    def light_powered_on(self, power_on=True):
        if power_on:
            self._send_command('<%s;LIGHT;PWR;ON>' % self.name)
        else:
            self._send_command('<%s;LIGHT;PWR;OFF>' % self.name)

    def light_toggle(self):
        """Toggle power state of light."""
        self.light_powered_on = not self.light_powered_on

    @staticmethod
    def listen(cycles=30):
        """Listen for broadcasts and logs them for debugging purposes.

        Listens for cycles iterations
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', 31415))
        for x in range(1, cycles):
            m = sock.recvfrom(1024)
            LOGGER.info(m)

    def discover_single_device(self):
        """Discover a single device.

        Called during __init__ if the device name or IP address is missing.

        This function will discover only the first device to respond if both
        name and IP were not provided on instantiation. If there is only one
        device in the home this will work well. Otherwise, use the discover
        function of the module rather than this one.
        """
        data = '<ALL;DEVICE;ID;GET>'.encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LOGGER.debug("Sending broadcast.")
        s.sendto(data, ('<broadcast>', self.PORT))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LOGGER.debug("Listening...")
        try:
            s.bind(('', self.PORT))
        except OSError as e:
            # Address already in use
            LOGGER.exception("Port is in use or could not be opened."
                             "Is another instance running?")
            raise OSError
        else:
            try:
                m = s.recvfrom(1024)
                LOGGER.info(m)
                if not m:
                    LOGGER.error("Didn't receive response.")
                else:
                    self.details = m[0].decode('utf-8')
                    res = re.match(
                        '\((.*);DEVICE;ID;(.*);(.*),(.*)\)', self.details)
                    # TODO: Parse this properly rather than regex
                    self.name = res.group(1)
                    self.mac = res.group(2)
                    self.model = res.group(3)
                    self.series = res.group(4)
                    self.ip = m[1][0]
                    LOGGER.info(self.name, self.mac, self.model, self.series)
            except OSError as e:
                LOGGER.critical("No device was found.\n%s" % e)
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
            LOGGER.info('Status: ' + status)
        except socket.timeout:
            LOGGER.error('Socket Timed Out')
        else:
            # TODO: this function shouldn't return data OR False, handle this better
            sock.close()
            LOGGER.info(str(status))
            match_obj = re.match('\(.*;([^;]+)\)', status)
            if match_obj:
                return match_obj.group(1)
            else:
                return False

    def send_raw(self, msg):
        """Send a raw command. Device name is not included.

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
        timeout_occurred = False
        while True:
            try:
                recv = sock.recv(1048).decode('utf-8')
                LOGGER.info('Status: ' + recv)
                messages.append(recv)
            except socket.timeout:
                LOGGER.info('Socket Timed Out')
                # most likely this means no more data, give it one more iter
                if timeout_occurred:
                    break
                else:
                    timeout_occurred = True
            else:
                LOGGER.info(str(recv))
        sock.close()
        return messages

    @MWT(timeout=45)
    def _get_all_request(self):
        """Get all parameters from device, returns as a list."""
        results = self.send_raw('<%s;GETALL>' % self.name)
        # sometimes this gets two sections in one string:
        # join list to str, clean up (), and split back to a list
        return '||'.join(results).replace('(', '').replace(')', '').split('||')

    def _get_all(self):
        """Get all parameters from the fan <%s;GETALL>.

        This, due to Haiku's API not returning all parameters, but it gets most
        of them.

        Method is marked internal, but could be useful for troubleshooting.
        Suggested way to get to this data is to use the get_attribute method.
        Requesting the desired parameter.

        This data is cached for 30 seconds to avoid the ten seconds it takes to
        run and to reduce requests sent to the fan.

        :return: List of [almost] all fan data.
        """
        # if monitor running, send cache, if not do request
        if self._monitoring and self._all_cache:
            return self._all_cache
        else:
            return self._get_all_bare()

    def _get_all_bare(self):
        res_dict = {}
        results = self._get_all_request()
        for result in results:
            # remove device name i.e Living Room Fan
            _, result = result.split(';', 1)

            # handle these manually due to multiple values in result
            # FAN and LIGHT both have BOOKENDS attributes
            if 'BOOKENDS' in result:
                device, low, high = result.rsplit(';', 2)
                res_dict[device] = (low, high)
            elif 'NW;PARAMS;ACTUAL' in result:
                # ip, subnet, gateway
                res_dict['NW;PARAMS;ACTUAL'] = (result.rsplit(';', 3))[1:]
            else:
                category, value = result.rsplit(';', 1)
                res_dict[category] = value
        self._all_cache = res_dict
        return res_dict

    def get_attribute(self, attribute):
        """Given a string in the format NW;PARAMS;ACTUAL return parameter value.

        There is a 30 second cache on the GETALL that this pulls from to speed
        things up and to avoid hammering the fan with requests.

        Raises KeyError if key doesn't exist

        See KNOWN_ATTRIBUTES for full list of known attributes

        Anything handled specifically in a property is better retrieved that
        way as it returns within a second, as where this will usually take ten
        seconds if not cached.

        Example:
          get_attribute('NW;PARAMS;ACTUAL')
          ['192.168.1.50', '255.255.255.0', '192.168.1.1']
        :param attribute: The attribute you seek
        :return: The value you find
        """
        if attribute == 'SNSROCC;STATUS':  # doesn't get retrieeved in get_all
            return self._query('<%s;SNSROCC;STATUS;GET>' % self.name)
        else:
            response_dict = self._get_all()
        return response_dict[attribute]

    def _get_all_nested(self):
        def nest(existing, keys, value):
            key, *keys = keys
            if keys:
                if key not in existing:
                    existing[key] = {}
                nest(existing[key], keys, value)
            else:
                existing[key] = value

        results = self._get_all_request()
        # fix double results
        extra_rows = []
        for result in results:
            if ')(' in result:
                halves = result.split(')(')
                # result = result.replace(halves[1], ')')
                extra_rows.append(halves[1])
        results.extend(extra_rows)
        cleaned = [x.replace('(', '').replace(')', '') for x in results]

        for idx, result in enumerate(cleaned):
            if 'BOOKENDS' in result:
                device, low, high = result.rsplit(';', 2)
                cleaned[idx] = '{};{},{}'.format(device, low, high)
            elif 'NW;PARAMS;ACTUAL' in result:
                nw_params_actual, ip, sn, gw = result.rsplit(';', 3)
                cleaned[idx] = '{};{},{},{}'.format(
                    nw_params_actual, ip, sn, gw)

        data = [x.split(';')[1:] for x in cleaned]
        d = {}
        for *keys, value in data:
            nest(d, keys, value)
        return d

    @property
    def json(self):
        """Export all fan details to json."""
        return json.dumps(self._get_all_nested())

    @property
    def xml(self):
        """Export all fan details to xml."""
        return data_to_xml(self._get_all_nested()).decode()

    @property
    def dict(self):
        """Export all fan details as dict."""
        return self._get_all_nested()

    @property
    def flat_dict(self):
        """Export all fan details as a flat dict."""
        return self._get_all()

    @staticmethod
    def _parse_values(line):
        if len(line.rsplit(';', 1)) > 1:
            k, v = line.rsplit(';', 1)
            return k, v

    def start_monitor(self):
        """Start the monitor.

        Starts a monitor that gets all attributes from the fan every
        monitor_frequency seconds.

        Using this makes all queries, after first monitor iteration, instant.
        """
        # TODO: See above
        if not self._monitoring:
            self._monitoring = True
            self._background_monitor.start()

    def stop_monitor(self):
        """Stop the monitor."""
        self._monitoring = False
        self._background_monitor.stop()


def discover(devices_to_find=3, time_to_wait=5):
    """Discover SenseMe devices.

    :return: List of discovered SenseMe devices.
    """
    port = 31415

    data = '<ALL;DEVICE;ID;GET>'.encode('utf-8')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    LOGGER.debug("Sending broadcast.")
    s.sendto(data, ('<broadcast>', port))
    LOGGER.debug("Listening...")
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
                LOGGER.info("Received a message")
                message_decoded = message[0].decode('utf-8')
                res = re.match(
                    '\((.*);DEVICE;ID;(.*);(.*),(.*)\)', message_decoded)
                # TODO: Parse this properly rather than regex
                name = res.group(1)
                mac = res.group(2)
                model = res.group(3)
                series = res.group(4)
                ip = message[1][0]
                devices.append(
                    SenseMe(ip=ip, name=name, model=model,
                            series=series, mac=mac))

            time.sleep(.5)
            if start_time + time_to_wait < time.time() or \
               len(devices) >= devices_to_find:
                LOGGER.debug("time_to_wait exceeded or devices_to_find met")
                break
        return devices
    except OSError:
        # couldn't get port
        raise OSError("Couldn't get port 31415")
    finally:
        s.close()
