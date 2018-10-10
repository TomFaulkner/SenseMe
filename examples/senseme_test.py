import optparse

from senseme import SenseMe, discover



def main():
    """A script that exposes all of the senseme commands as a CLI to enable scripting"""
    fan = None
    parser = optparse.OptionParser()
    fan_group = optparse.OptionGroup(parser, "Commands specific to the fan")
    addon_light_group = optparse.OptionGroup(
        parser, "Commands specific to the add on light to the fan"
    )
    wall_controller_group = optparse.OptionGroup(
        parser, "Commands specific to the wall controller"
    )
    device_group = optparse.OptionGroup(parser, "Commands generic to senseme devices")
    device_group.add_option("--ip", default=None, help="IP Address of Fan")
    device_group.add_option(
        "--name", default=None, help="Name of SenseMe Device as from the Haiku App"
    )
    device_group.add_option(
        "--model", default="FAN", help="Model of the SenseMe device"
    )
    device_group.add_option(
        "--get-beeper-sound",
        default=None,
        action="store_true",
        help="Returns if the beeper sound is ON or OFF",
    )
    device_group.add_option(
        "--set-beeper-sound", default=None, help="Sets beepersound to ON or OFF"
    )
    device_group.add_option(
        "--get-device-time",
        default=None,
        action="store_true",
        help="Returns the present time on the device",
    )
    device_group.add_option(
        "--get-firmware-name",
        default=None,
        action="store_true",
        help="Returns the name of the presently running firmware",
    )
    device_group.add_option(
        "--get-firmware-version",
        default=None,
        action="store_true",
        help="Returns the version of the presently running firmware",
    )
    device_group.add_option(
        "--list-devices",
        default=None,
        action="store_true",
        help="listens on the local network for Haiku devices and prints information about them.",
    )
    device_group.add_option(
        "--get-led-indicators",
        default=None,
        action="store_true",
        help="Returns if the indicator leds are ON or OFF",
    )
    device_group.add_option(
        "--set-led-indicators",
        default=None,
        help="Sets if the indicator leds are ON or OFF",
    )
    device_group.add_option(
        "--get-network-apstatus",
        default=None,
        action="store_true",
        help="Returns if the wireless access point is enabled on the device",
    )
    device_group.add_option(
        "--get-network-dhcp-state",
        default=None,
        action="store_true",
        help="Returns if the device is running a local dhcp service",
    )
    device_group.add_option(
        "--get-network-parameters",
        default=None,
        action="store_true",
        help="Return a string of all network settings for the device",
    )
    device_group.add_option(
        "--get-network-ssid",
        default=None,
        action="store_true",
        help="Return the wireless SSID the device is connected to",
    )
    device_group.add_option(
        "--get-network-token",
        default=None,
        action="store_true",
        help="Return the network token of the device",
    )
    fan_group.add_option(
        "--get-fanmode",
        default=None,
        action="store_true",
        help="Returns if the light is ON or OFF",
    )
    fan_group.add_option(
        "--set-fanmode", default=None, help="Sets the fan to ON or OFF"
    )
    fan_group.add_option(
        "--toggle-fanmode",
        default=None,
        action="store_true",
        help="Toggles the fan mode between ON or OFF",
    )
    fan_group.add_option(
        "--get-height",
        default=None,
        action="store_true",
        help="retrieve the height of the fan in centimeters",
    )
    fan_group.add_option(
        "--set-height",
        default=None,
        type=int,
        help="Sets the height of the fan in centimeters (ex. 10ft=304)",
    )
    fan_group.add_option(
        "--get-speed",
        default=None,
        action="store_true",
        help="retrieve the speed of the fan (0-7)",
    )
    fan_group.add_option(
        "--set-speed", default=None, type="int", help="set the speed of the fan (0-7)"
    )
    fan_group.add_option(
        "--get-minspeed",
        default=None,
        action="store_true",
        help="Returns the fan's minimum speed setting (0-7)",
    )
    fan_group.add_option(
        "--get-maxspeed",
        default=None,
        action="store_true",
        help="Returns the fan's maximum speed setting (0-7)",
    )
    fan_group.add_option(
        "--get-room-fanspeed-limits",
        default=None,
        action="store_true",
        help="Returns the fans min and max speeds for the room settings.",
    )
    fan_group.add_option(
        "--set-room-fanspeed-limits",
        default=None,
        nargs=2,
        dest="roomfanspeedlimits",
        help="Sets the fans min and max speeds for the room settings. "
        "This take 2 arguments min max with each being (0-7)",
    )
    fan_group.add_option(
        "--decrease-fanspeed",
        default=None,
        action="store_true",
        help="Decreases the speed of the fan by 1",
    )
    fan_group.add_option(
        "--increase-fanspeed",
        default=None,
        action="store_true",
        help="increases the speed of the fan by 1",
    )
    fan_group.add_option(
        "--get-learnmode",
        default=None,
        action="store_true",
        help="Returns if the fan's learning mode is ON or OFF",
    )
    fan_group.add_option(
        "--set-learnmode",
        default=None,
        help="Sets if the fan's learning mode is ON or OFF",
    )
    fan_group.add_option(
        "--get-learnmode-zerotemp",
        default=None,
        action="store_true",
        help="Returns the temp in fahrenheit where learning mode "
        "auto-shuts off the fan (valid temps 50-90)",
    )
    fan_group.add_option(
        "--set-learnmode-zerotemp",
        default=None,
        type="int",
        help="Sets the temp in fahrenheit where learning mode "
        "auto-shuts off the fan (valid temps 50-90)",
    )
    fan_group.add_option(
        "--get-learnmode-minspeed",
        default=None,
        action="store_true",
        help="Returns the minimum speed setting for learning mode (0-7)",
    )
    fan_group.add_option(
        "--set-learnmode-minspeed",
        default=None,
        type="int",
        help="Sets the minimum speed setting for learning mode (0-7)",
    )
    fan_group.add_option(
        "--get-learnmode-maxspeed",
        default=None,
        action="store_true",
        help="Sets the maximum speed setting for learning mode (0-7)",
    )
    fan_group.add_option(
        "--set-learnmode-maxspeed",
        default=None,
        type="int",
        help="Sets the maximum speed setting for learning mode (0-7)",
    )
    fan_group.add_option(
        "--get-smartsleep-mode",
        default=None,
        action="store_true",
        help="Returns if the fan's smartsleep mode is ON or OFF",
    )
    fan_group.add_option(
        "--set-smartsleep-mode",
        default=None,
        help="Sets if the fan's smartsleep mode is ON or OFF",
    )
    fan_group.add_option(
        "--get-smartsleep-idealtemp",
        default=None,
        action="store_true",
        help="retrieve the smart sleep mode ideal temp in fahrenheit",
    )
    fan_group.add_option(
        "--set-smartsleep-idealtemp",
        default=None,
        type="int",
        help="Sets the smart sleep mode ideal temp in fahrenheit (valid temps 50-90)",
    )
    fan_group.add_option(
        "--get-smartsleep-minspeed",
        default=None,
        action="store_true",
        help="retrieve the minimum the speed of the fan (0-7) when in smartsleep mode",
    )
    fan_group.add_option(
        "--set-smartsleep-minspeed",
        default=None,
        type="int",
        help="set the minimum speed of the fan (0-7) when in smartsleep mode",
    )
    fan_group.add_option(
        "--get-smartsleep-maxspeed",
        default=None,
        action="store_true",
        help="retrieve the maximum the speed of the fan (0-7) when in smartsleep mode",
    )
    fan_group.add_option(
        "--set-smartsleep-maxspeed",
        default=None,
        type="int",
        help="set the maximum speed of the fan (0-7) when in smartsleep mode",
    )
    fan_group.add_option(
        "--get-smartsleep-wakeup-brightness",
        default=None,
        action="store_true",
        help="get the add-on light brightness in wakeup mode "
        "(0-16) 0=off, 1-16 are the brightness levels",
    )
    fan_group.add_option(
        "--set-smartsleep-wakeup-brightness",
        default=None,
        type="int",
        help="set the add-on light brightness in wakeup mode "
        "(0-16) 0=off, 1-16 are the brightness levels",
    )
    fan_group.add_option(
        "--get-fan-direction",
        default=None,
        action="store_true",
        help="Gets if the fan blades are spinning forward or reverse.",
    )
    fan_group.add_option(
        "--set-fan-direction",
        default=None,
        help="Sets if the fan blades are spinning forward or reverse. DO NOT DO WITH BLADES SPINNING",
    )
    fan_group.add_option(
        "--get-fan-motionmode",
        default=None,
        action="store_true",
        help="Returns if the fan's motion sensor is ON or OFF",
    )
    fan_group.add_option(
        "--set-fan-motionmode",
        default=None,
        help="Sets if the fan's motion sensor is ON or OFF",
    )
    fan_group.add_option(
        "--get-motionmode-mintimer",
        default=None,
        action="store_true",
        help="Returns the minimum number of minutes the timer "
        "can be set to auto-shutoff the fan and/or add-on light",
    )
    fan_group.add_option(
        "--get-motionmode-maxtimer",
        default=None,
        action="store_true",
        help="Returns the maximum number of minutes the timer "
        "can be set to auto-shutoff the fan and/or add-on light",
    )
    fan_group.add_option(
        "--get-motionmode-currenttimer",
        default=None,
        action="store_true",
        help="Returns the current number of minutes the timer "
        "can be set to auto-shutoff the fan and/or add-on light",
    )
    fan_group.add_option(
        "--set-motionmode-timer",
        default=None,
        help="Sets the the number of minutes the timer "
        "will run prior to auto-shutoff of the fan and/or add-on light",
    )
    fan_group.add_option(
        "--get-motionmode-occupied-status",
        default=None,
        action="store_true",
        help="Returns if the room is presently occupied or "
        "unoccupied based on the built in motion sensor.",
    )
    fan_group.add_option(
        "--get-wintermode",
        default=None,
        action="store_true",
        help="Returns if the wintermode state is ON or OFF",
    )
    fan_group.add_option(
        "--set-wintermode", default=None, help="Sets wintermode to ON or OFF"
    )
    fan_group.add_option(
        "--get-smartmode",
        default=None,
        action="store_true",
        help="Returns if the smartmode is off, cooling or heating",
    )
    fan_group.add_option(
        "--set-smartmode",
        default=None,
        help="Sets smart mode to off,cooling, or heating",
    )
    fan_group.add_option(
        "--get-whooshmode",
        default=None,
        action="store_true",
        help="Returns of whoosh mode is ON or OFF",
    )
    fan_group.add_option(
        "--set-whooshmode", default=None, help="Sets whoosh mode to ON or OFF"
    )
    addon_light_group.add_option(
        "--get-brightness",
        default=None,
        action="store_true",
        help="retrieve the brightness of the fan (0-16)",
    )
    addon_light_group.add_option(
        "--set-brightness",
        default=None,
        type="int",
        help="Sets the brightness of the light on the fan (0-16)",
    )
    addon_light_group.add_option(
        "--get-min-brightness",
        default=None,
        action="store_true",
        help="Returns the add-on lights minimum brightness setting (0-16)",
    )
    addon_light_group.add_option(
        "--get-max-brightness",
        default=None,
        action="store_true",
        help="Returns the add-on lights maximum brightness setting (0-16)",
    )
    addon_light_group.add_option(
        "--get-room-brightness-limits",
        default=None,
        action="store_true",
        help="Returns the add-on lights min and max brightness for the room settings",
    )
    addon_light_group.add_option(
        "--set-room-brightness-limits",
        default=None,
        type="int",
        nargs=2,
        dest="roombrightnesslimits",
        help="Sets the add-on lights min and max brightness "
        "for the room settings this takes 2 arguments min max with each being (0-16)",
    )
    addon_light_group.add_option(
        "--decrease-brightness",
        default=None,
        action="store_true",
        help="Decreases the brightness of the light by 1",
    )
    addon_light_group.add_option(
        "--increase-brightness",
        default=None,
        action="store_true",
        help="increase the brightnes of the light by 1",
    )
    addon_light_group.add_option(
        "--is-fan-light-installed",
        default=None,
        action="store_true",
        help="Returns if the optional light module is present",
    )
    addon_light_group.add_option(
        "--get-light-motionmode",
        default=None,
        action="store_true",
        help="Returns if the light's motion sensor is ON or OFF",
    )
    addon_light_group.add_option(
        "--set-light-motionmode",
        default=None,
        help="Sets if the light's motion sensor is ON or OFF",
    )
    addon_light_group.add_option(
        "--get-lightmode",
        default=None,
        action="store_true",
        help="Returns if the light is ON or OFF",
    )
    addon_light_group.add_option(
        "--set-lightmode", default=None, help="Sets the light to ON or OFF"
    )
    addon_light_group.add_option(
        "--toggle-lightmode",
        default=None,
        action="store_true",
        help="Toggles the light mode between ON or OFF",
    )

    parser.add_option_group(device_group)
    parser.add_option_group(fan_group)
    parser.add_option_group(addon_light_group)
    parser.add_option_group(wall_controller_group)
    opts, args = parser.parse_args()

    if not all([opts.ip, opts.name]):
        print("IP and the fan name are required to work")
        return 1
    elif len(args) != 0:
        print("Unknown options specified: " + " ".join(args))
        return 1
    else:
        fan = SenseMe(ip=opts.ip, name=opts.name, model=opts.model)

    # Process all the command line arguments

    # Device commands first
    if opts.get_beeper_sound:
        mode = fan.beeper_sound
        print(mode)
        return 0
    elif opts.set_beeper_sound:
        mode = opts.set_beeper_sound.upper()
        if mode == "ON" or mode == "OFF":
            fan.beeper_sound = mode
            return 0
        else:
            print("Invalid beeper sound specified, valid option are ON or OFF")
            return 1
    elif opts.get_device_time:
        print(fan.device_time)
        return 0
    elif opts.get_firmware_name:
        print(fan.firmware_name)
        return 0
    elif opts.get_firmware_version:
        print(fan.firmware_version)
        return 0
    elif opts.list_devices:
        devices = discover()
        for device in devices:
            print(
                '%s,%s,%s,%s,"%s"'
                % (device.name, device.ip, device.mac, device.series, device.model)
            )
        return 0
    elif opts.get_led_indicators:
        mode = fan.led_indicators
        print(mode)
        return 0
    elif opts.set_led_indicators:
        mode = opts.set_led_indicators.upper()
        if mode == "OFF" or mode == "ON":
            fan.led_indicators = mode
            return 0
        else:
            print("Invalid led indicator state specified, valid option are ON or OFF")
            return 1
    elif opts.get_network_apstatus:
        print(fan.network_ap_status)
        return 0
    elif opts.get_network_dhcp_state:
        print(fan.network_dhcp_state)
        return 0
    elif opts.get_network_parameters:
        (ip, subnetmask, defaultgw) = fan.network_parameters
        print(ip + "," + subnetmask + "," + defaultgw)
        return 0
    elif opts.get_network_ssid:
        print(fan.network_ssid)
        return 0
    elif opts.get_network_token:
        print(fan.network_token)
        return 0

    # Fan commands
    elif opts.get_fanmode:
        mode = fan.fan_powered_on
        if mode:
            print("ON")
        else:
            print("OFF")
        return 0
    elif opts.set_fanmode:
        mode = opts.set_fanmode.upper()
        if mode == "ON":
            fan.fan_powered_on = True
        else:
            fan.fan_powered_on = False
        return 0
    elif opts.get_height:
        print(fan.height)
        return 0
    elif opts.set_height:
        if opts.set_height > 0:
            fan.height = opts.set_height
        return 0
    elif opts.toggle_fanmode:
        fan.fan_toggle()
        return 0
    elif opts.get_speed:
        print(fan.speed)
        return 0
    elif opts.set_speed is not None:
        if opts.set_speed >= 7:
            fan.speed = 7
        elif opts.set_speed <= 0:
            fan.speed = 0
        else:
            fan.speed = opts.set_speed
        return 0
    elif opts.get_minspeed:
        print(fan.min_speed)
        return 0
    elif opts.get_maxspeed:
        print(fan.max_speed)
        return 0
    elif opts.get_room_fanspeed_limits:
        (min_speed, max_speed) = fan.room_settings_fan_speed_limits
        print("%d %d" % (min_speed, max_speed))
    elif opts.roomfanspeedlimits:
        min_speed = opts.roomfanspeedlimits[0]
        max_speed = opts.roomfanspeedlimits[1]
        fan.room_settings_fan_speed_limits = (min_speed, max_speed)
    elif opts.decrease_fanspeed:
        fan.dec_speed()
        return 0
    elif opts.increase_fanspeed:
        fan.inc_speed()
        return 0
    elif opts.get_learnmode:
        mode = fan.learnmode
        print(mode.upper())
        return 0
    elif opts.set_learnmode:
        mode = opts.set_learnmode.upper()
        if mode == "OFF" or mode == "ON":
            fan.learnmode = mode
            return 0
        else:
            print("Invalid learn mode specified, valid option are ON or OFF")
            return 1
    elif opts.get_learnmode_zerotemp:
        print(fan.learnmode_zerotemp)
        return 0
    elif opts.set_learnmode_zerotemp:
        if opts.set_learnmode_zerotemp >= 90:
            fan.learn_mode_zero_temp = 90
        elif opts.set_learnmode_zerotemp <= 50:
            fan.learnmode_zerotemp = 50
        else:
            fan.learnmode_zerotemp = opts.set_learnmode_zero_temp
        return 0
    elif opts.get_learnmode_minspeed:
        print(fan.learnmode_minspeed)
        return 0
    elif opts.set_learnmode_minspeed is not None:
        if opts.set_learnmode_minspeed >= 7:
            fan.learnmode_minspeed = 7
        elif opts.set_learnmode_minspeed <= 0:
            fan.learnmode_minspeed = 0
        else:
            fan.learnmode_minspeed = opts.set_learnmode_minspeed
        return 0
    elif opts.get_learnmode_maxspeed:
        print(fan.learnmode_maxspeed)
        return 0
    elif opts.set_learnmode_maxspeed is not None:
        if opts.set_learnmode_maxspeed >= 7:
            fan.learnmode_maxspeed = 7
        elif opts.set_learnmode_maxspeed <= 0:
            fan.learnmode_maxspeed = 0
        else:
            fan.learnmode_maxspeed = opts.set_learnmode_maxspeed
        return 0
    elif opts.get_smartsleep_mode:
        mode = fan.smartsleep_mode
        print(mode.upper())
        return 0
    elif opts.set_smartsleep_mode:
        mode = opts.set_smartsleep_mode.upper()
        if mode == "OFF" or mode == "ON":
            fan.smartsleep_mode = mode
            return 0
        else:
            print("Invalid smartsleep mode specified, valid option are ON or OFF")
            return 1
    elif opts.get_smartsleep_idealtemp:
        print(fan.smartsleep_idealtemp)
        return 0
    elif opts.set_smartsleep_idealtemp:
        if opts.set_smartsleep_idealtemp >= 90:
            fan.smartsleep_idealtemp = 90
        elif opts.set_smartsleep_idealtemp <= 50:
            fan.smartsleep_idealtemp = 50
        else:
            fan.smartsleep_idealtemp = opts.set_smartsleep_idealtemp
        return 0
    elif opts.get_smartsleep_minspeed:
        print(fan.smartsleep_minspeed)
        return 0
    elif opts.set_smartsleep_minspeed is not None:
        if opts.set_smartsleep_minspeed >= 7:
            fan.smartsleep_minspeed = 7
        elif opts.set_smartsleep_minspeed <= 0:
            fan.smartsleep_minspeed = 0
        else:
            fan.smartsleep_minspeed = opts.set_smartsleep_minspeed
        return 0
    elif opts.get_smartsleep_maxspeed:
        print(fan.smartsleep_maxspeed)
        return 0
    elif opts.set_smartsleep_maxspeed is not None:
        if opts.set_smartsleep_maxspeed >= 7:
            fan.smartsleep_maxspeed = 7
        elif opts.set_smartsleep_maxspeed <= 0:
            fan.smartsleep_maxspeed = 0
        else:
            fan.smartsleep_maxspeed = opts.set_smartsleep_maxspeed
        return 0
    elif opts.get_smartsleep_wakeup_brightness:
        print(fan.smartsleep_wakeup_brightness)
        return 0
    elif opts.set_smartsleep_wakeup_brightness is not None:
        if opts.set_smartsleep_wakeup_brightness >= 16:
            fan.smartsleep_wakeup_brightness = 16
        elif opts.set_smartsleep_wakeup_brightness <= 0:
            fan.smartsleep_wakeup_brightness = 0
        else:
            fan.smartsleep_wakeup_brightness = opts.set_smartsleep_wakeup_brightness
        return 0
    elif opts.get_fan_direction:
        mode = fan.fan_direction
        if mode.upper() == "FWD":
            print("FORWARD")
        else:
            print("REVERSE")
        return 0
    elif opts.set_fan_direction:
        mode = opts.set_fan_direction.upper()
        if mode == "FORWARD":
            fan.fan_direction = "FWD"
            return 0
        elif mode == "REVERSE":
            fan.fan_direction = "REV"
            return 0
        else:
            print(
                "Invalid fan direction specified, valid option are FORWARD or REVERSE"
            )
            return 1
    elif opts.get_fan_motionmode:
        mode = fan.fan_motionmode
        print(mode.upper())
        return 0
    elif opts.set_fan_motionmode:
        mode = opts.set_fan_motionmode.upper()
        if mode == "OFF" or mode == "ON":
            fan.fan_motionmode = mode
            return 0
        else:
            print(
                "Invalid fan motion detection mode specified, valid option are ON or OFF"
            )
            return 1
    elif opts.get_motionmode_mintimer:
        print(fan.motionmode_mintimer)
        return 0
    elif opts.get_motionmode_maxtimer:
        print(fan.motionmode_maxtimer)
        return 0
    elif opts.get_motionmode_currenttimer:
        print(fan.motionmode_currenttimer)
        return 0
    elif opts.set_motionmode_timer:
        fan.motionmode_currenttimer = opts.set_motionmode_timer
        return 1
    elif opts.get_motionmode_occupied_status:
        mode = fan.motionmode_occupied_status
        print(mode.upper())
        return 0
    elif opts.get_wintermode:
        mode = fan.wintermode
        print(mode)
        return 0
    elif opts.set_wintermode:
        mode = opts.set_wintermode.upper()
        if mode == "OFF" or mode == "ON":
            fan.wintermode = mode
            return 0
        else:
            print("Invalid winter mode specified, valid option are ON or OFF")
            return 1
    elif opts.get_smartmode:
        mode = fan.smartmode
        print(mode)
        return 0
    elif opts.set_smartmode:
        mode = opts.set_smartmode.upper()
        if mode == "OFF" or mode == "COOLING" or mode == "HEATING":
            fan.smartmode = mode
            return 0
        else:
            print(
                "Invalid smart mode specified, valid option are OFF, COOLING or HEATING"
            )
            return 1
    elif opts.get_whooshmode:
        mode = fan.whoosh
        if mode:
            print("ON")
        else:
            print("OFF")
        return 0
    elif opts.set_whooshmode:
        mode = opts.set_whooshmode.upper()
        if mode == "ON":
            fan.whoosh = True
        else:
            fan.whoosh = False
        return 0

    # Add-on Light Commands
    elif opts.get_brightness:
        print(fan.brightness)
        return 0
    elif opts.set_brightness is not None:
        if opts.set_brightness >= 16:
            fan.brightness = 16
        elif opts.set_brightness <= 0:
            fan.brightness = 0
        else:
            fan.brightness = opts.set_brightness
        return 0
    elif opts.get_min_brightness:
        print(fan.min_brightness)
        return 0
    elif opts.get_max_brightness:
        print(fan.max_brightness)
        return 0
    elif opts.get_room_brightness_limits:
        (min_brightness, max_brightness) = fan.room_settings_brightness_limits
        print("%d %d" % (min_brightness, max_brightness))
        return 0
    elif opts.roombrightnesslimits:
        min_brightness = opts.room_brightness_limits[0]
        max_brightness = opts.room_brightness_limits[1]
        fan.room_settings_brightness_limits = (min_brightness, max_brightness)
        return 0
    elif opts.decrease_brightness:
        fan.dec_brightness()
        return 0
    elif opts.increase_brightness:
        fan.inc_brightness()
        return 0
    elif opts.is_fan_light_installed:
        mode = fan.is_fan_light_installed
        if mode:
            print("INSTALLED")
            return 1
        else:
            print("NOT INSTALLED")
        return 0
    elif opts.get_light_motionmode:
        mode = fan.light_motionmode
        print(mode.upper())
        return 0
    elif opts.set_light_motionmode:
        mode = opts.set_light_motionmode.upper()
        if mode == "OFF" or mode == "ON":
            fan.light_motionmode = mode
            return 0
        else:
            print(
                "Invalid light motion detection mode specified, valid option are ON or OFF"
            )
            return 1
    elif opts.get_lightmode:
        mode = fan.light_powered_on
        if mode:
            print("ON")
        else:
            print("OFF")
        return 0
    elif opts.set_lightmode:
        mode = opts.set_lightmode.upper()
        if mode == "ON":
            fan.light_powered_on = True
        else:
            fan.light_powered_on = False
        return 0
    elif opts.toggle_lightmode:
        fan.light_toggle()
        return 0
    else:
        print("Invalid argument specified")
        return 1


if __name__ == "__main__":
    main()
