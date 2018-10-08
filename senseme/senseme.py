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
import math

from .lib import MWT, BackgroundLoop
from .lib.xml import data_to_xml

LOGGER = logging.getLogger(__name__)

__author__ = "Tom Faulkner"
__url__ = "https://github.com/TomFaulkner/SenseMe/"


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

    def __init__(self, ip="", name="", model="", series="", mac="", **kwargs):
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
            self.details = ""
            self.model = model
            self.series = series
        self.monitor_frequency = kwargs.get("monitor_frequency", 45)
        self._monitoring = False
        self._all_cache = None

        self._background_monitor = BackgroundLoop(
            self.monitor_frequency, self._get_all_bare
        )
        if kwargs.get("monitor", False):
            self.start_monitor()

    def __repr__(self):
        """Repr Method."""
        return (
            f"SenseMe(name='{self.name}', ip='{self.ip}', "
            f"model='{self.model}', series='{self.series}', "
            f"mac='{self.mac}')"
        )

    def __str__(self):
        """Str Method."""
        return (
            f"SenseMe Device: {self.name}, Series: {self.series}. "
            f"(Speed: {self.speed}. Brightness: {self.brightness})"
        )

    # The following properties are generic to haiku devices

    @property
    def beeper_sound(self):
        """Returns if the audible beeper sound is ON or OFF"""
        return self._query("<%s;DEVICE;BEEPER;GET>" % self.name)

    @beeper_sound.setter
    def beeper_sound(self, mode):
        """
        Sets the audible beeper sound to ON or OFF

        :param mode: valid values are ON and OFF
        """
        mode = mode.upper()
        if mode != "OFF" and mode != "ON":
            LOGGER.debug("%s is an invalid beeper sound setting.  Use ON or OFF" % mode)
        else:
            self._send_command("<%s;DEVICE;BEEPER;%s>" % (self.name, mode))
            self._update_cache("DEVICE;BEEPER", mode)

    @property
    def device_time(self):
        """Return the current time on the device"""
        return self._query("<%s;TIME;VALUE;GET>" % self.name)

    @property
    def firmware_name(self):
        """Return the name of the firmware file running on the SenseMe device"""
        return self._query("<%s;FW;NAME;GET>" % self.name)

    @property
    def firmware_version(self):
        """Return the name of the firmware running on the fan"""
        name = self.firmware_name
        return self._query("<%s;FW;%s;GET>" % (self.name, name))

    @property
    def led_indicators(self):
        """Returns if the fan's indicator LED is ON or OFF"""
        return self._query("<%s;DEVICE;INDICATORS;GET>" % self.name)

    @led_indicators.setter
    def led_indicators(self, mode):
        """
        Sets the fan's indicator LED to ON or OFF

        :param mode: valid values are ON and OFF
        """
        mode = mode.upper()
        if mode != "OFF" and mode != "ON":
            LOGGER.debug("%s is an led indicator setting.  Use ON or OFF" % mode)
        else:
            self._send_command("<%s;DEVICE;INDICATORS;%s>" % (self.name, mode))
            self._update_cache("DEVICE;INDICATORS", mode)

    @property
    def network_ap_status(self):
        """Returns if the wireless access point is enabled on the device"""
        return self._query("<%s;NW;AP;GET;STATUS>" % self.name)

    @property
    def network_dhcp_state(self):
        """Returns if the device is running a local dhcp service"""
        return self._query("<%s;NW;DHCP;GET>" % self.name)

    @property
    def network_parameters(self):
        """
        Return a string of all network settings for the device

        The string is of the form IP Address;Subnet Mask;Default Gateway
        """
        raw = self._queryraw("<%s;NW;PARAMS;GET;ACTUAL>" % self.name)

        # grab all between the parens
        raw = raw[raw.find("(") + 1 : raw.find(")")]

        vals = raw.split(";")
        return vals[4], vals[5], vals[6]

    @property
    def network_ssid(self):
        """Return the wireless SSID the device is connected to"""
        return self._query("<%s;NW;SSID;GET>" % self.name)

    @property
    def network_token(self):
        """Return the network token of the device"""
        return self._query("<%s;NW;TOKEN;GET>" % self.name)

    # The following properties are specific to haiku fans
    @property
    def fan_powered_on(self):
        """
        Returns if the fan is on or off

        Power On = True
        Power Off = False
        """
        if self._query("<%s;FAN;PWR;GET>" % self.name) == "ON":
            return True
        else:
            return False

    @fan_powered_on.setter
    def fan_powered_on(self, power_on=True):
        """
        Sets the fan to be on or off

        :param power_on: True=On, False=Off
        """
        if power_on:
            self._send_command("<%s;FAN;PWR;ON>" % self.name)
            self._update_cache("FAN;PWR", "ON")
        else:
            self._send_command("<%s;FAN;PWR;OFF>" % self.name)
            self._update_cache("FAN;PWR", "OFF")

    def fan_toggle(self):
        """Toggle power state of fan."""
        self.fan_powered_on = not self.fan_powered_on

    @property
    def height(self):
        """Returns/sets fan height in centimeters"""
        return int(self._query("<%s;WINTERMODE;HEIGHT;GET>" % self.name))

    @height.setter
    def height(self, val):
        """
        Sets fan height in centimeters

        :param val: The height in centimeters
        """
        if val > 0:
            self._send_command("<%s;WINTERMODE;HEIGHT;SET;%s>" % (self.name, val))
            self._update_cache("WINTERMODE;HEIGHT", str(val))

    @property
    def speed(self):
        """Returns the fan speed."""
        # loop and exception handling due to:
        # https://github.com/TomFaulkner/SenseMe/issues/38
        for _ in range(2):
            speed = self._query("<%s;FAN;SPD;GET;ACTUAL>" % self.name)
            LOGGER.debug(speed)
            try:
                return int(speed)
            except ValueError:
                if speed == "OFF":
                    return 0
        return 0  # return something rather than cause an exception

    @speed.setter
    def speed(self, speed):
        """
        Sets fan speed.

        :param val: Valid values are between 0 and 7.
        """
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0
        self._send_command("<%s;FAN;SPD;SET;%s>" % (self.name, speed))
        self._update_cache("FAN;SPD;ACTUAL", str(speed))

    @property
    def min_speed(self):
        """Returns the fan's minimum speed setting."""
        return self._query("<%s;FAN;SPD;GET;MIN>" % self.name)

    @property
    def max_speed(self):
        """Returns the fan's maximum speed setting."""
        return self._query("<%s;FAN;SPD;GET;MAX>" % self.name)

    @property
    def room_settings_fan_speed_limits(self):
        """Returns a tuple of the min and max fan speeds the room is configured to support"""
        raw = self._queryraw("<%s;FAN;BOOKENDS;GET>" % self.name)

        # grab all between the parens
        raw = raw[raw.find("(") + 1 : raw.find(")")]

        vals = raw.split(";")
        return int(vals[3]), int(vals[4])

    @room_settings_fan_speed_limits.setter
    def room_settings_fan_speed_limits(self, speeds):
        """
        Set a tuple of the min and max fan speeds the room is configured to support

        :params speeds: [min,max]
        """
        if speeds[0] >= speeds[1]:
            LOGGER.debug("min speed cannot exceed max speed")
            return

        self._send_command(
            "<%s;FAN;BOOKENDS;SET;%s;%s>" % (self.name, speeds[0], speeds[1])
        )

    def dec_speed(self, decrement=1):
        """ Decreases fan speed by decrement value, default is 1."""
        self.speed -= decrement

    def inc_speed(self, increment=1):
        """Increases fan speed by increment value, default is 1."""
        self.speed += increment

    @property
    def learnmode(self):
        """Returns/sets the fan's wintermode setting."""
        mode = self._query("<%s;LEARN;STATE;GET>" % self.name).upper()
        if mode == "LEARN":
            return "ON"
        else:
            return mode

    @learnmode.setter
    def learnmode(self, mode):
        """
        Returns/sets the fan's wintermode setting.

        :params mode: valid values are OFF and ON
        """
        mode = mode.upper()
        if mode == "ON":
            mode = "LEARN"
        elif mode != "OFF":
            LOGGER.error("%s is an invalid learn mode" % mode)

        self._send_command("<%s;LEARN;STATE;SET;%s>" % (self.name, mode))
        self._update_cache("LEARN;STATE", mode)

    @property
    def learnmode_zerotemp(self):
        """Returns the temperature in fahrenheit that the fan will auto shutoff"""
        temp = self._query("<%s;LEARN;ZEROTEMP;GET>" % self.name)
        return math.ceil(((int(temp) * 9) / 500) + 32)

    @learnmode_zerotemp.setter
    def learnmode_zerotemp(self, temp):
        """
        Sets the temperature in fahrenheit that the fan will auto shutoff

        :params temp: valid values are 50-90
        """
        if temp < 50:
            temp = 50
        elif temp > 90:
            temp = 90

        temp = int((((int(temp) - 32) * 500) / 9))
        self._send_command("<%s;LEARN;ZEROTEMP;SET;%s>" % (self.name, temp))
        self._update_cache("LEARN;ZEROTEMP", temp)

    @property
    def learnmode_minspeed(self):
        """Returns the fan's minimum speed setting in learning mode."""
        return self._query("<%s;LEARN;MINSPEED;GET>" % self.name)

    @learnmode_minspeed.setter
    def learnmode_minspeed(self, speed):
        """
        Sets the fan's minimum speed setting in learning mode.

        :param speed: valid values are 0-7
        """
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0

        self._send_command("<%s;LEARN;MINSPEED;SET;%s>" % (self.name, speed))
        self._update_cache("LEARN;MINSPEED", speed)

    @property
    def learnmode_maxspeed(self):
        """Returns the fan's maximum speed setting."""
        return self._query("<%s;LEARN;MAXSPEED;GET>" % self.name)

    @learnmode_maxspeed.setter
    def learnmode_maxspeed(self, speed):
        """
        Sets the fan's minimum speed setting in learning mode.

        :param speed: valid values are 0-7
        """
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0

        self._send_command("<%s;LEARN;MAXSPEED;SET;%s>" % (self.name, speed))
        self._update_cache("LEARN;MAXSPEED", speed)

    @property
    def smartsleep_mode(self):
        """Returns the fan's smart sleep mode setting."""
        return self._query("<%s;SLEEP;STATE;GET>" % self.name)

    @smartsleep_mode.setter
    def smartsleep_mode(self, mode):
        """
        Sets the fan's smart sleep mode setting.

        :param mode: valid values are ON and OFF
        """
        mode = mode.upper()
        if mode != "ON" and mode != "OFF":
             LOGGER.error(
                "%s is an invalid sleep mode. Valid values are ON and OFF" % mode
            )

        self._send_command("<%s;SLEEP;STATE;%s>" % (self.name, mode))
        self._update_cache("SLEEP;STATE", mode)

    @property
    def smartsleep_idealtemp(self):
        """Returns the fan's smart sleep ideal temp setting."""
        temp = self._query("<%s;SMARTSLEEP;IDEALTEMP;GET>" % self.name)

        return math.ceil(((int(temp) * 9) / 500) + 32)

    @smartsleep_idealtemp.setter
    def smartsleep_idealtemp(self, temp):
        """
        Sets the fan's smart sleep ideal temp setting.

        :param temp: valid values are 50-90 degrees fahrenheit
        """
        if temp < 50:
            temp = 50
        elif temp > 90:
            temp = 90

        temp = int((((int(temp) - 32) * 500) / 9))
        self._send_command("<%s;SMARTSLEEP;IDEALTEMP;SET;%s>" % (self.name, temp))
        self._update_cache("SMARTSLEEP;IDEALTEMP", temp)

    @property
    def smartsleep_minspeed(self):
        """ Returns the fan's smartsleep minimum speedsetting."""
        return self._query("<%s;SMARTSLEEP;MINSPEED;GET>" % self.name)

    @smartsleep_minspeed.setter
    def smartsleep_minspeed(self, speed):
        """
        Returns/sets the fan's smartsleep minimum speedsetting.

        :params speed: valid values are 0-7
        """
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0

        self._send_command("<%s;SMARTSLEEP;MINSPEED;SET;%s>" % (self.name, speed))
        self._update_cache("SMARTSLEEP;MINSPEED", speed)

    @property
    def smartsleep_maxspeed(self):
        """Returns the fan's smart sleep minimum speed setting."""
        return self._query("<%s;SMARTSLEEP;MAXSPEED;GET>" % self.name)

    @smartsleep_maxspeed.setter
    def smartsleep_maxspeed(self, speed):
        """
        Sets the fan's smart sleep maximum speed setting.

        :param speed: valid values are 0-7
        """
        if speed > 7:  # max speed is 7, fan corrects to 7
            speed = 7
        elif speed < 0:  # 0 also sets fan to off automatically
            speed = 0

        self._send_command("<%s;SMARTSLEEP;MAXSPEED;SET;%s>" % (self.name, speed))
        self._update_cache("SMARTSLEEP;MAXSPEED", speed)

    """
    Returns/sets light brightness at wakeup for sleep mode

    Valid values are between 0 and 16.
    0 is off, 16 is max.
    """

    @property
    def smartsleep_wakeup_brightness(self):
        """Returns light brightness at wakeup for sleep mode"""
        result = self._query("<%s;SLEEP;EVENT;OFF;GET>" % self.name)
        if (result == "LIGHT,PWR,OFF") or (result == "OFF"):
            return 0
        else:
            return int(result.replace("LIGHT,LEVEL,", ""))

    @smartsleep_wakeup_brightness.setter
    def smartsleep_wakeup_brightness(self, light):
        """
        Sets light brightness at wakeup for sleep mode

        :param light: Valid values are between 0 and 16.
        """
        if light > 16:
            light = 16
        elif light < 0:
            light = 0
        self._send_command(
            "<%s;SLEEP;EVENT;OFF;SET;LIGHT,LEVEL,%s>" % (self.name, light)
        )
        self._update_cache("SLEEP;EVENT;OFF;LIGHT,LEVEL,", str(light))

    @property
    def fan_direction(self):
        """Returns the direction of the fan"""
        return self._query("<%s;FAN;DIR;GET>" % self.name)

    @fan_direction.setter
    def fan_direction(self, mode):
        """
        Sets the direction of the fan rotation

        :params mode: Valid values are FWD and REV
        """
        mode = mode.upper()

        if mode != "FWD" and mode != "REV":
            LOGGER.error(
                "%s is an invalid direction.  Valid values are FWD and REV" % mode
            )
        else:
            self._send_command("<%s;FAN;DIR;SET;%s>" % (self.name, mode))
            self._update_cache("FAN;DIR", mode)

    @property
    def fan_motionmode(self):
        """Returns the fan motion sensor mode"""
        return self._query("<%s;FAN;AUTO;GET>" % self.name)

    @fan_motionmode.setter
    def fan_motionmode(self, mode):
        """
        Sets the fan motion sensor mode

        :param mode: valid values are ON and OFF
        """
        mode = mode.upper()
        if mode != "OFF" and mode != "ON":
            LOGGER.error(
                "%s is an invalid fan motion mode.  Valid modes are ON and OFF" % mode
            )
        else:
            self._send_command("<%s;FAN;AUTO;SET;%s>" % (self.name, mode))
            self._update_cache("FAN;AUTO", mode)

    @property
    def motionmode_mintimer(self):
        """Returns the minimum timer setting in minutes for the fan and light auto shutoff on no motion."""
        timer = self._query("<%s;SNSROCC;TIMEOUT;GET;MIN>" % self.name)
        return int(int(timer) / 60000)

    @property
    def motionmode_maxtimer(self):
        """Returns the minimum timer setting in minutes for the fan and light auto shutoff on no motion."""
        timer = self._query("<%s;SNSROCC;TIMEOUT;GET;MAX>" % self.name)
        return int(int(timer) / 60000)

    @property
    def motionmode_currenttimer(self):
        """Returns the current timer setting in minutes for the fan and light auto shutoff on no motion."""
        timer = self._query("<%s;SNSROCC;TIMEOUT;GET;CURR>" % self.name)
        return int(int(timer) / 60000)

    @motionmode_currenttimer.setter
    def motionmode_currenttimer(self, timeout):
        """Sets the timout setting in minutes for the fan and light auto shutoff on no motion."""
        self._send_command("<%s;SNSROCC;TIMEOUT;SET;%s>" % (self.name, int(int(timeout)*60000)))
        self._update_cache("SNSROCC;TIMEOUT", timeout)

    @property
    def motionmode_occupied_status(self):
        """Returns  if the room is currently OCCUPIED or UNOCCUPIED based on the motion sensor in the fan."""
        return self._query("<%s;SNSROCC;STATUS;GET>" % self.name)

    @property
    def wintermode(self):
        """Returns the fan's winter mode setting."""
        return self._query("<%s;WINTERMODE;STATE;GET>" % self.name)

    @wintermode.setter
    def wintermode(self, mode):
        """
        Returns/sets the fan's winter mode setting.

        :param mode: valid values are OFF and ON
        """
        mode = mode.upper()
        if mode != "OFF" and mode != "ON":
            LOGGER.error(
                "%s is an invalid winter mode. Valid modes are ON and OFF" % mode
            )
        else:
            self._send_command("<%s;WINTERMODE;STATE;%s>" % (self.name, mode))
            self._update_cache("WINTERMODE;STATE", mode)

    @property
    def smartmode(self):
        """Returns the fan's smart mode setting."""
        return self._query("<%s;SMARTMODE;STATE;GET>" % self.name)

    @smartmode.setter
    def smartmode(self, mode):
        """
        Sets the fan's smartmode setting.

        :param mode: valid values are OFF, COOLING, and HEATING
        """
        mode = mode.upper()
        if mode != "OFF" and mode != "COOLING" and mode != " HEATING":
            LOGGER.error("%s is an invalid smartmode" % mode)

        self._send_command("<%s;SMARTMODE;STATE;SET;%s>" % (self.name, mode))
        self._update_cache("SMARTMODE;ACTUAL", mode)

    @property
    def whoosh(self):
        """Retrieve whoosh mode.

        This can have a ten second delay since there is no known one item
        request to retrieve status
        """
        try:
            if self.get_attribute("FAN;WHOOSH;STATUS") == "ON":
                return True
            else:
                return False
        except KeyError:
            LOGGER.error("FAN;WHOOSH;STATUS wasn't found in dict")
            raise OSError("Fan failed to return whoosh status")

    @whoosh.setter
    def whoosh(self, whoosh_on):
        """Set the whoosh mode.

        This can have a ten second delay since there is no known one item
        request to retrieve status

        :param whoosh_on: valid values are True or False
        """
        if whoosh_on:
            self._send_command("<%s;FAN;WHOOSH;ON>" % self.name)
            self._update_cache("FAN;WHOOSH;STATUS", "ON")
        else:
            self._send_command("<%s;FAN;WHOOSH;OFF>" % self.name)
            self._update_cache("FAN;WHOOSH;STATUS", "OFF")

    # The following properties are specific to haiku fans
    # add-on light modules.  Most of these apply to the
    # standalone light units as well

    @property
    def brightness(self):
        """Returns light brightness."""
        # workaround for https://github.com/TomFaulkner/SenseMe/issues/38
        for _ in range(2):
            result = self._query("<%s;LIGHT;LEVEL;GET;ACTUAL>" % self.name)
            try:
                return int(result)
            except ValueError:
                if result == "OFF":
                    return 0
        return 0  # return something rather than cause an exception

    @brightness.setter
    def brightness(self, light):
        """
        Sets light brightness.

        :param lightL Valid values are between 0 and 16.
        """
        if light > 16:
            light = 16
        elif light < 0:
            light = 0
        self._send_command("<%s;LIGHT;LEVEL;SET;%s>" % (self.name, light))
        self._update_cache("LIGHT;LEVEL;ACTUAL", str(light))

    @property
    def min_brightness(self):
        """Returns the add-on lights minimum brightness setting."""
        brightness = self._query("<%s;LIGHT;LEVEL;GET;MIN>" % self.name)
        LOGGER.debug(brightness)

        return brightness

    @min_brightness.setter
    def min_brightness(self, light):
        """
        Sets the add-on lights minimum brightness setting.

        :param light: valid values are 0-16
        """
        if light > 16:
            light = 16
        elif light < 0:
            light = 0

        self._send_command("<%s;LIGHT;LEVEL;MIN;%s>" % (self.name, light))
        self._update_cache("LIGHT;LEVEL;MIN", light)

    @property
    def max_brightness(self):
        """Returns the add-on lights maximum brightness setting."""
        return int(self._query("<%s;LIGHT;LEVEL;GET;MAX>" % self.name))

    @max_brightness.setter
    def max_brightness(self, light):
        """
        Sets the add-on lights maximum brightness setting.

        :param light: valid values are 0-16
        """
        if light > 16:
            light = 16
        elif light < 0:
            light = 0

        self._send_command("<%s;LIGHT;LEVEL;MAX;%s>" % (self.name, light))
        self._update_cache("LIGHT;LEVEL;MAX", light)

    @property
    def room_settings_brightness_limits(self):
        """Returns a tuple of the min and max light brightnesses the room supports"""
        raw = self._queryraw("<%s;LIGHT;BOOKENDS;GET>" % self.name)

        # grab all between the parens
        raw = raw[raw.find("(") + 1 : raw.find(")")]

        vals = raw.split(";")
        return int(vals[3]), int(vals[4])

    @room_settings_brightness_limits.setter
    def room_settings_brightness_limits(self, limits):
        """
        Sets a tuple of the min and max light brightnesses the room supports

        :params limits: [min,max]
        """
        if limits[0] >= limits[1]:
            LOGGER.debug("minbrightness cannot exceed maxbrightness")
        self._send_command(
            "<%s;LIGHT;BOOKENDS;SET;%s;%s>" % (self.name, limits[0], limits[1])
        )

    def dec_brightness(self, decrement=1):
        """
        Decreases fan speed by decrement value, default is 1.

        :param decrement: number of steps to decrement with the call
        """
        self.brightness -= decrement

    def inc_brightness(self, increment=1):
        """
        Increases brightness by increment value, default is 1.

        :param increment: number of steps to increment with the call
        """
        self.brightness += increment

    @property
    def is_fan_light_installed(self):
        """
         Returns if the optional light module is installed in the fan

         :return True if present or False if not
         """
        mode = self._query("<%s;DEVICE;LIGHT;GET>" % self.name)
        return mode.lower() == "present"

    @property
    def light_motionmode(self):
        """Returns the if the add on light responds to the motion sensor"""
        return self._query("<%s;LIGHT;AUTO;GET>" % self.name)

    @light_motionmode.setter
    def light_motionmode(self, mode):
        """
        Sets the if the add on light responds to the motion sensor

        :params mode: valid values are OFF and ON
        """
        mode = mode.upper()
        if mode != "ON" and mode != "OFF":
            LOGGER.error("%s is an invalid light motion mode" % mode)
        else:
            self._send_command("<%s;LIGHT;AUTO;%s>" % (self.name, mode))
            self._update_cache("LIGHT;AUTO", mode)

    @property
    def light_powered_on(self):
        """Returns True if the lige is on False if its off"""
        if self._query("<%s;LIGHT;PWR;GET>" % self.name) == "ON":
            return True
        return False

    @light_powered_on.setter
    def light_powered_on(self, power_on=True):
        """
        Turns the addon light module on or off

        :param power_on: True equals on, False equals off
        """
        if power_on:
            self._send_command("<%s;LIGHT;PWR;ON>" % self.name)
            self._update_cache("LIGHT;PWR", "ON")
        else:
            self._send_command("<%s;LIGHT;PWR;OFF>" % self.name)
            self._update_cache("LIGHT;PWR", "OFF")

    def light_toggle(self):
        """Toggle power state of light."""
        self.light_powered_on = not self.light_powered_on

    @staticmethod
    def listen(cycles=30):
        """Listen for broadcasts and logs them for debugging purposes.

        Listens for cycles iterations
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 31415))
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
        data = "<ALL;DEVICE;ID;GET>".encode("utf-8")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LOGGER.debug("Sending broadcast.")
        s.sendto(data, ("<broadcast>", self.PORT))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LOGGER.debug("Listening...")
        try:
            s.bind(("", self.PORT))
        except OSError as e:
            # Address already in use
            LOGGER.exception(
                "Port is in use or could not be opened." "Is another instance running?"
            )
            raise OSError
        else:
            try:
                m = s.recvfrom(1024)
                LOGGER.info(m)
                if not m:
                    LOGGER.error("Didn't receive response.")
                else:
                    self.details = m[0].decode("utf-8")
                    res = re.match("\((.*);DEVICE;ID;(.*);(.*),(.*)\)", self.details)
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
        sock.send(msg.encode("utf-8"))
        sock.close()

    def _query(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode("utf-8"))

        try:
            status = sock.recv(1048).decode("utf-8")
            LOGGER.info("Status: " + status)
        except socket.timeout:
            LOGGER.error("Socket Timed Out")
        else:
            # TODO: this shouldn't return data OR False, handle this better
            sock.close()
            LOGGER.info(str(status))
            match_obj = re.match("\(.*;([^;]+)\)", status)
            if match_obj:
                return match_obj.group(1)
            else:
                return False

    """
    This is a hack to deal with the NW;PARAM command returning a multi-value
    it needs better clean up if SenseMe starts using that pattern more often
    """

    def _queryraw(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode("utf-8"))

        try:
            status = sock.recv(1048).decode("utf-8")
            LOGGER.info("Status: " + status)
        except socket.timeout:
            LOGGER.error("Socket Timed Out")
        else:
            # TODO: this shouldn't return data OR False, handle this better
            sock.close()
            LOGGER.info(str(status))
            return status

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
        sock.send(msg.encode("utf-8"))

        messages = []
        timeout_occurred = False
        while True:
            try:
                recv = sock.recv(1048).decode("utf-8")
                LOGGER.info("Status: " + recv)
                messages.append(recv)
            except socket.timeout:
                LOGGER.info("Socket Timed Out")
                # most likely this means no more data, give it one more iter
                if timeout_occurred:
                    break
                else:
                    timeout_occurred = True
            else:
                LOGGER.info(str(recv))
        sock.close()
        return messages

    def _update_cache(self, attribute, value):
        """Update an attribute in the cache with a new value.

        Allows the cache to keep up with changes made by _send_command().
        Looks for attribute changes that affect other attributes and
        updates them too.

        :param attribute: cache attribute to update
        :param value: new attribute value
        """
        if self._monitoring and self._all_cache:
            # update cache attribute with new value
            self._all_cache[attribute] = value
            # check for attribute changes that affect other attributes
            # this list is not exhaustive and there may be other attributes
            # with the propensity to affect it's neighbors
            if attribute == "FAN;PWR":
                # changes to fan power also affects fan speed and whoosh
                if value == "OFF":
                    self._all_cache["FAN;SPD;ACTUAL"] = "0"
                    self._all_cache["FAN;WHOOSH;STATUS"] = "OFF"
            elif attribute == "FAN;SPD;ACTUAL":
                # changes to fan speed also affects fan power and whoosh status
                if int(value) == 0:
                    self._all_cache["FAN;PWR"] = "OFF"
                    self._all_cache["FAN;WHOOSH;STATUS"] = "OFF"
                else:
                    self._all_cache["FAN;PWR"] = "ON"
            elif attribute == "LIGHT;PWR":
                # changes to light power also affects light brightness
                if value == "OFF":
                    self._all_cache["LIGHT;LEVEL;ACTUAL"] = "0"
            elif attribute == "LIGHT;LEVEL;ACTUAL":
                # changes to light brightness also changes light power
                if int(value) > 0:
                    self._all_cache["LIGHT;PWR"] = "ON"
                else:
                    self._all_cache["LIGHT;PWR"] = "OFF"

    @MWT(timeout=45)
    def _get_all_request(self):
        """Get all parameters from device, returns as a list."""
        results = self.send_raw("<%s;GETALL>" % self.name)
        # sometimes this gets two sections in one string:
        # join list to str, clean up (), and split back to a list
        results = "||".join(results).replace(")(", ")||(")
        return results.replace("(", "").replace(")", "").split("||")

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
            _, result = result.split(";", 1)

            # handle these manually due to multiple values in result
            # FAN and LIGHT both have BOOKENDS attributes
            if "BOOKENDS" in result:
                device, low, high = result.rsplit(";", 2)
                res_dict[device] = (low, high)
            elif "NW;PARAMS;ACTUAL" in result:
                # ip, subnet, gateway
                res_dict["NW;PARAMS;ACTUAL"] = (result.rsplit(";", 3))[1:]
            else:
                category, value = result.rsplit(";", 1)
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
        if attribute == "SNSROCC;STATUS":  # doesn't get retrieved in get_all
            return self._query("<%s;SNSROCC;STATUS;GET>" % self.name)
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
            if ")(" in result:
                halves = result.split(")(")
                # result = result.replace(halves[1], ')')
                extra_rows.append(halves[1])
        results.extend(extra_rows)
        cleaned = [x.replace("(", "").replace(")", "") for x in results]

        for idx, result in enumerate(cleaned):
            if "BOOKENDS" in result:
                device, low, high = result.rsplit(";", 2)
                cleaned[idx] = "{};{},{}".format(device, low, high)
            elif "NW;PARAMS;ACTUAL" in result:
                nw_params_actual, ip, sn, gw = result.rsplit(";", 3)
                cleaned[idx] = "{};{},{},{}".format(nw_params_actual, ip, sn, gw)

        data = [x.split(";")[1:] for x in cleaned]
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
        if len(line.rsplit(";", 1)) > 1:
            k, v = line.rsplit(";", 1)
            return k, v

    def start_monitor(self):
        """Start the monitor.

        Starts a monitor that gets all attributes from the fan every
        monitor_frequency seconds.

        Using this makes all queries, after first monitor iteration, instant.
        """
        if not self._monitoring:
            self._monitoring = True
            self._background_monitor.start()

    def stop_monitor(self):
        """Stop the monitor."""
        self._monitoring = False
        self._background_monitor.stop()


def discover(devices_to_find=6, time_to_wait=5):
    """Discover SenseMe devices.

    :return: List of discovered SenseMe devices.
    """
    port = 31415

    data = "<ALL;DEVICE;ID;GET>".encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    LOGGER.debug("Sending broadcast.")
    s.sendto(data, ("<broadcast>", port))
    LOGGER.debug("Listening...")
    devices = []
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("", port))
        s.settimeout(2)
        while True:
            try:
                message = s.recvfrom(1024)
            except OSError:
                # timeout occurred
                message = b""
            if message:
                LOGGER.info("Received a message")
                message_decoded = message[0].decode("utf-8")
                res = re.match("\((.*);DEVICE;ID;(.*);(.*),(.*)\)", message_decoded)
                # TODO: Parse this properly rather than regex
                name = res.group(1)
                mac = res.group(2)
                model = res.group(3)
                series = res.group(4)
                ip = message[1][0]
                devices.append(
                    SenseMe(ip=ip, name=name, model=model, series=series, mac=mac)
                )

            time.sleep(0.5)
            if (
                start_time + time_to_wait < time.time()
                or len(devices) >= devices_to_find
            ):
                LOGGER.debug("time_to_wait exceeded or devices_to_find met")
                break
        return devices
    except OSError:
        # couldn't get port
        raise OSError("Couldn't get port 31415")
    finally:
        s.close()

    @staticmethod
    def listen(cycles=30):
        """Listen for broadcasts and logs them for debugging purposes.

        Listens for cycles iterations
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 31415))
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
        data = "<ALL;DEVICE;ID;GET>".encode("utf-8")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        LOGGER.debug("Sending broadcast.")
        s.sendto(data, ("<broadcast>", self.PORT))

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        LOGGER.debug("Listening...")
        try:
            s.bind(("", self.PORT))
        except OSError as e:
            # Address already in use
            LOGGER.exception(
                "Port is in use or could not be opened." "Is another instance running?"
            )
            raise OSError
        else:
            try:
                m = s.recvfrom(1024)
                LOGGER.info(m)
                if not m:
                    LOGGER.error("Didn't receive response.")
                else:
                    self.details = m[0].decode("utf-8")
                    res = re.match("\((.*);DEVICE;ID;(.*);(.*),(.*)\)", self.details)
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
        sock.send(msg.encode("utf-8"))
        sock.close()

    def _query(self, msg):
        sock = socket.socket()
        sock.settimeout(5)

        sock.connect((self.ip, self.PORT))
        sock.send(msg.encode("utf-8"))

        try:
            status = sock.recv(1048).decode("utf-8")
            LOGGER.info("Status: " + status)
        except socket.timeout:
            LOGGER.error("Socket Timed Out")
        else:
            # TODO: this shouldn't return data OR False, handle this better
            sock.close()
            LOGGER.info(str(status))
            match_obj = re.match("\(.*;([^;]+)\)", status)
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
        sock.send(msg.encode("utf-8"))

        messages = []
        timeout_occurred = False
        while True:
            try:
                recv = sock.recv(1048).decode("utf-8")
                LOGGER.info("Status: " + recv)
                messages.append(recv)
            except socket.timeout:
                LOGGER.info("Socket Timed Out")
                # most likely this means no more data, give it one more iter
                if timeout_occurred:
                    break
                else:
                    timeout_occurred = True
            else:
                LOGGER.info(str(recv))
        sock.close()
        return messages

    def _update_cache(self, attribute, value):
        """Update an attribute in the cache with a new value.

        Allows the cache to keep up with changes made by _send_command().
        Looks for attribute changes that affect other attributes and
        updates them too.

        :param attribute: cache attribute to update
        :param value: new attribute value
        """
        if self._monitoring and self._all_cache:
            # update cache attribute with new value
            self._all_cache[attribute] = value
            # check for attribute changes that affect other attributes
            # this list is not exhaustive and there may be other attributes
            # with the propensity to affect it's neighbors
            if attribute == "FAN;PWR":
                # changes to fan power also affects fan speed and whoosh
                if value == "OFF":
                    self._all_cache["FAN;SPD;ACTUAL"] = "0"
                    self._all_cache["FAN;WHOOSH;STATUS"] = "OFF"
            elif attribute == "FAN;SPD;ACTUAL":
                # changes to fan speed also affects fan power and whoosh status
                if int(value) == 0:
                    self._all_cache["FAN;PWR"] = "OFF"
                    self._all_cache["FAN;WHOOSH;STATUS"] = "OFF"
                else:
                    self._all_cache["FAN;PWR"] = "ON"
            elif attribute == "LIGHT;PWR":
                # changes to light power also affects light brightness
                if value == "OFF":
                    self._all_cache["LIGHT;LEVEL;ACTUAL"] = "0"
            elif attribute == "LIGHT;LEVEL;ACTUAL":
                # changes to light brightness also changes light power
                if int(value) > 0:
                    self._all_cache["LIGHT;PWR"] = "ON"
                else:
                    self._all_cache["LIGHT;PWR"] = "OFF"

    @MWT(timeout=45)
    def _get_all_request(self):
        """Get all parameters from device, returns as a list."""
        results = self.send_raw("<%s;GETALL>" % self.name)
        # sometimes this gets two sections in one string:
        # join list to str, clean up (), and split back to a list
        results = "||".join(results).replace(")(", ")||(")
        return results.replace("(", "").replace(")", "").split("||")

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
            _, result = result.split(";", 1)

            # handle these manually due to multiple values in result
            # FAN and LIGHT both have BOOKENDS attributes
            if "BOOKENDS" in result:
                device, low, high = result.rsplit(";", 2)
                res_dict[device] = (low, high)
            elif "NW;PARAMS;ACTUAL" in result:
                # ip, subnet, gateway
                res_dict["NW;PARAMS;ACTUAL"] = (result.rsplit(";", 3))[1:]
            else:
                category, value = result.rsplit(";", 1)
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
        if attribute == "SNSROCC;STATUS":  # doesn't get retrieeved in get_all
            return self._query("<%s;SNSROCC;STATUS;GET>" % self.name)
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
            if ")(" in result:
                halves = result.split(")(")
                # result = result.replace(halves[1], ')')
                extra_rows.append(halves[1])
        results.extend(extra_rows)
        cleaned = [x.replace("(", "").replace(")", "") for x in results]

        for idx, result in enumerate(cleaned):
            if "BOOKENDS" in result:
                device, low, high = result.rsplit(";", 2)
                cleaned[idx] = "{};{},{}".format(device, low, high)
            elif "NW;PARAMS;ACTUAL" in result:
                nw_params_actual, ip, sn, gw = result.rsplit(";", 3)
                cleaned[idx] = "{};{},{},{}".format(nw_params_actual, ip, sn, gw)

        data = [x.split(";")[1:] for x in cleaned]
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
        if len(line.rsplit(";", 1)) > 1:
            k, v = line.rsplit(";", 1)
            return k, v

    def start_monitor(self):
        """Start the monitor.

        Starts a monitor that gets all attributes from the fan every
        monitor_frequency seconds.

        Using this makes all queries, after first monitor iteration, instant.
        """
        if not self._monitoring:
            self._monitoring = True
            self._background_monitor.start()

    def stop_monitor(self):
        """Stop the monitor."""
        self._monitoring = False
        self._background_monitor.stop()


def discover(devices_to_find=6, time_to_wait=5):
    """Discover SenseMe devices.

    :return: List of discovered SenseMe devices.
    """
    port = 31415

    data = "<ALL;DEVICE;ID;GET>".encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    LOGGER.debug("Sending broadcast.")
    s.sendto(data, ("<broadcast>", port))
    LOGGER.debug("Listening...")
    devices = []
    start_time = time.time()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(("", port))
        s.settimeout(2)
        while True:
            try:
                message = s.recvfrom(1024)
            except OSError:
                # timeout occurred
                message = b""
            if message:
                LOGGER.info("Received a message")
                message_decoded = message[0].decode("utf-8")
                res = re.match("\((.*);DEVICE;ID;(.*);(.*),(.*)\)", message_decoded)
                # TODO: Parse this properly rather than regex
                name = res.group(1)
                mac = res.group(2)
                model = res.group(3)
                series = res.group(4)
                ip = message[1][0]
                devices.append(
                    SenseMe(ip=ip, name=name, model=model, series=series, mac=mac)
                )

            time.sleep(0.5)
            if (
                start_time + time_to_wait < time.time()
                or len(devices) >= devices_to_find
            ):
                LOGGER.debug("time_to_wait exceeded or devices_to_find met")
                break
        return devices
    except OSError:
        # couldn't get port
        raise OSError("Couldn't get port 31415")
    finally:
        s.close()
