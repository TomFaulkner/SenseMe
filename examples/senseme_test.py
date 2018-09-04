from senseme import SenseMe
from senseme import discover
import optparse
import sys


def main():
    fan = None
    parser = optparse.OptionParser()
    fangroup = optparse.OptionGroup(parser, 'Commands specific to the fan')
    lightgroup = optparse.OptionGroup(parser,
                            'Commands specific to the standalone light')
    addonlightgroup = optparse.OptionGroup(parser,
                            'Commands specific to the add on light to the fan')
    wallcontrollergroup = optparse.OptionGroup(parser,
                            'Commands specific to the wall controller')
    devicegroup = optparse.OptionGroup(parser,
                            'Commands generic to senseme devices')

    devicegroup.add_option('--ip',   default=None, help="IP Address of Fan")
    devicegroup.add_option('--name', default=None,
                      help="Name of SenseMe Device as from the Haiku App")
    devicegroup.add_option('--model', default="FAN",
                      help="Model of the SenseMe device")
    devicegroup.add_option('--get-beepersound', default=None, action='store_true',
                      help="Returns if the beeper sound is on or off")
    devicegroup.add_option('--set-beepersound', default=None,
                      help="Sets beepersound to on or off")
    devicegroup.add_option('--get-devicetime', default=None, action='store_true',
                      help="Returns the present time on the device")
    devicegroup.add_option('--get-firmwarename', default=None, action='store_true',
                      help="Returns the name of the presently running firmware")
    devicegroup.add_option('--get-firmwareversion', default=None, action='store_true',
                      help="Returns the version of the presently running firmware")
    devicegroup.add_option('--list-devices', default=None, action='store_true',
                      help="listens on the local network for Haiku devices "
                            "and prints information about them.")
    devicegroup.add_option('--get-ledindicators', default=None, action='store_true',
                      help="Returns if the indicator leds are on or off")
    devicegroup.add_option('--set-ledindicators', default=None,
                      help="Sets if the indicator leds are on or off")
    devicegroup.add_option('--get-networkapstatus', default=None, action='store_true',
                      help="Returns if the wireless access point is enabled "
                           "on the device")
    devicegroup.add_option('--get-networkdhcpstate', default=None, action='store_true',
                      help="Returns if the device is running a local "
                           "dhcp service")
    devicegroup.add_option('--get-networkparameters', default=None, action='store_true',
                      help="Return a string of all network settings for "
                           "the device")
    devicegroup.add_option('--get-networkssid', default=None, action='store_true',
                      help="Return the wireless SSID the device is connected "
                           "to")
    devicegroup.add_option('--get-networktoken', default=None, action='store_true',
                      help="Return the network token of the device")

    fangroup.add_option('--get-fanmode', default=None, action='store_true',
                      help="Returns if the light is on or off")
    fangroup.add_option('--set-fanmode', default=None,
                      help="Sets the fan to on or off")
    fangroup.add_option('--toggle-fanmode', default=None, action='store_true',
                      help="Toggles the fan mode between on or off")
    fangroup.add_option('--get-height', default=None, action='store_true',
                      help="retrieve the height of the fan in centimeters")
    fangroup.add_option('--set-height', default=None, type=int,
                      help="Sets the height of the fan in centimeters "
                      "(ex. 10ft=304)")
    fangroup.add_option('--get-speed', default=None, action='store_true',
                      help="retrieve the speed of the fan (0-7)")
    fangroup.add_option('--set-speed', default=None, type="int",
                      help="set the speed of the fan (0-7)")
    fangroup.add_option('--get-minspeed', default=None, action='store_true',
                      help="Returns the fan's minimum speed setting (0-7)")
    fangroup.add_option('--get-maxspeed', default=None, action='store_true',
                      help="Returns the fan's maximum speed setting (0-7)")
    fangroup.add_option('--get-roomfanspeedlimits', default=None,
                        action='store_true',
                        help="Returns the fans min and max speeds for the room settings.")
    fangroup.add_option('--set-roomfanspeedlimits', default=None,
            nargs=2, dest='roomfanspeedlimits',
            help="Sets the fans min and max speeds for the room settings. "
                  "This take 2 arguments min max with each being (0-7)")
    fangroup.add_option('--decrease-fanspeed', default=None, action='store_true',
                      help="Decreases the speed of the fan by 1")
    fangroup.add_option('--increase-fanspeed', default=None, action='store_true',
                      help="increases the speed of the fan by 1")
    fangroup.add_option('--get-learnmode', default=None, action='store_true',
                      help="Returns if the fan's learning mode is on or off")
    fangroup.add_option('--set-learnmode', default=None,
                      help="Sets if the fan's learning mode is on or off")
    fangroup.add_option('--get-learnmodezerotemp', default=None,
                      action='store_true',
                      help="Returns the temp in fahrenheit where learning mode "
                      "auto-shuts off the fan (valid temps 50-90)")
    fangroup.add_option('--set-learnmodezerotemp', default=None, type="int",
                      help="Sets the temp in fahrenheit where learning mode "
                      "auto-shuts off the fan (valid temps 50-90)")
    fangroup.add_option('--get-learnmodeminspeed', default=None, action='store_true',
                      help="Returns the minimum speed setting for learning mode (0-7)")
    fangroup.add_option('--set-learnmodeminspeed', default=None, type='int',
                      help="Sets the minimum speed setting for learning mode (0-7)")
    fangroup.add_option('--get-learnmodemaxspeed', default=None, action='store_true',
                      help="Sets the maximum speed setting for learning mode (0-7)")
    fangroup.add_option('--set-learnmodemaxspeed', default=None, type='int',
                      help="Sets the maximum speed setting for learning mode (0-7)")
    fangroup.add_option('--get-smartsleepmode', default=None, action='store_true',
                      help="Returns if the fan's smartsleep mode is on or off")
    fangroup.add_option('--set-smartsleepmode', default=None,
                      help="Sets if the fan's smartsleep mode is on or off")
    fangroup.add_option('--get-smartsleepidealtemp', default=None, action='store_true',
                      help="retrieve the smart sleep mode ideal temp in "
                      "fahrenheit")
    fangroup.add_option('--set-smartsleepidealtemp', default=None, type="int",
                      help="Sets the smart sleep mode ideal temp in "
                      "fahrenheit (valid temps 50-90)")
    fangroup.add_option('--get-smartsleepminspeed', default=None, action='store_true',
                      help="retrieve the minimum the speed of the fan (0-7) "
                      "when in smartsleep mode")
    fangroup.add_option('--set-smartsleepminspeed', default=None, type="int",
                      help="set the minimum speed of the fan (0-7) when in "
                      "smartsleep mode")
    fangroup.add_option('--get-smartsleepmaxspeed', default=None, action='store_true',
                      help="retrieve the maximum the speed of the fan (0-7) "
                      "when in smartsleep mode")
    fangroup.add_option('--set-smartsleepmaxspeed', default=None, type="int",
                      help="set the maximum speed of the fan (0-7) when in "
                      "smartsleep mode")
    fangroup.add_option('--get-smartsleepwakeupbrightness', default=None,
                      action='store_true',
                      help="get the add-on light brightness in wakeup mode "
                      "(0-16) 0=off, 1-16 are the brightness levels")
    fangroup.add_option('--set-smartsleepwakeupbrightness', default=None, type="int",
                      help="set the add-on light brightness in wakeup mode "
                      "(0-16) 0=off, 1-16 are the brightness levels")
    fangroup.add_option('--get-fandirection', default=None, action='store_true',
                      help="Gets if the fan blades are spinning forward or "
                      "reverse.")
    fangroup.add_option('--set-fandirection', default=None,
                      help="Sets if the fan blades are spinning forward or "
                      "reverse.  DO NOT DO WITH BLADES SPINNING")
    fangroup.add_option('--get-fanmotionmode', default=None, action='store_true',
                      help="Returns if the fan's motion sensor is on or off")
    fangroup.add_option('--set-fanmotionmode', default=None,
                      help="Sets if the fan's motion sensor is on or off")
    fangroup.add_option('--get-motionmodemintimer', default=None, action='store_true',
                      help="Returns the minimum number of minutes the timer "
                      "can be set to auto-shutoff the fan and/or add-on light")
    fangroup.add_option('--get-motionmodemaxtimer', default=None, action='store_true',
                      help="Returns the maximum number of minutes the timer "
                      "can be set to auto-shutoff the fan and/or add-on light")
    fangroup.add_option('--get-motionmodecurrenttimer', default=None, action='store_true',
                      help="Returns the current number of minutes the timer "
                      "can be set to auto-shutoff the fan and/or add-on light")
    fangroup.add_option('--get-motionmodeoccupiedstatus', default=None, action='store_true',
                      help="Returns if the room is presently occupied or "
                      "unoccupied based on the built in motion sensor.")
    fangroup.add_option('--get-wintermode', default=None, action='store_true',
                      help="Returns if the wintermode state is on or off")
    fangroup.add_option('--set-wintermode', default=None,
                      help="Sets wintermode to on or off")
    fangroup.add_option('--get-smartmode', default=None, action='store_true',
                      help="Returns if the smartmode is off, cooling or heating")
    fangroup.add_option('--set-smartmode', default=None,
                      help="Sets smart mode to off,cooling, or heating")
    fangroup.add_option('--get-whooshmode', default=None, action='store_true',
                      help="Returns of whoosh mode is on or off")
    fangroup.add_option('--set-whooshmode', default=None,
                      help="Sets whoosh mode to on or off")          
    addonlightgroup.add_option('--get-brightness', default=None, action='store_true',
                      help="retrieve the brightness of the fan (0-16)")
    addonlightgroup.add_option('--set-brightness', default=None, type="int",
                      help="Sets the brightness of the light on the fan (0-16)")
    addonlightgroup.add_option('--get-minbrightness', default=None, action='store_true',
                      help="Returns the add-on lights minimum brightness "
                      "setting (0-16)")
    addonlightgroup.add_option('--get-maxbrightness', default=None, action='store_true',
                      help="Returns the add-on lights maximum brightness "
                      "setting (0-16)")
    addonlightgroup.add_option('--get-roombrightnesslimits', default=None,
                    action='store_true',
                    help="Returns the add-on lights min and max brightness "
                    "for the room settings")
    addonlightgroup.add_option('--set-roombrightnesslimits', default=None, type='int',
                    nargs=2, dest='roombrightnesslimits',
                    help="Sets the add-on lights min and max brightness "
                    "for the room settings this takes 2 arguments min max"
                    "with each being (0-16)")
    addonlightgroup.add_option('--decrease-brightness', default=None, action='store_true',
                      help="Decreases the brightness of the light by 1")
    addonlightgroup.add_option('--increase-brightness', default=None, action='store_true',
                      help="increase the brightnes of the light by 1")
    addonlightgroup.add_option('--isfanlightinstalled', default=None, action='store_true',
                      help="Returns if the optional light module is present")
    addonlightgroup.add_option('--get-lightmotionmode', default=None, action='store_true',
                      help="Returns if the light's motion sensor is on or off")
    addonlightgroup.add_option('--set-lightmotionmode', default=None,
                      help="Sets if the light's motion sensor is on or off")
    addonlightgroup.add_option('--get-lightmode', default=None, action='store_true',
                      help="Returns if the light is on or off")
    addonlightgroup.add_option('--set-lightmode', default=None,
                      help="Sets the light to on or off")
    addonlightgroup.add_option('--toggle-lightmode', default=None, action='store_true',
                      help="Toggles the light mode between on or off")
    lightgroup.add_option('--get-lighthue', default=None, action='store_true',
                      help="Returns the hue of the standalone light \
                       (valid values are between 2200-5000)")
    lightgroup.add_option('--set-lighthue', default=None,
                      help="Sets the fan to on or off")
    lightgroup.add_option('--islightcolor', default=None, action='store_true',
                      help="Returns if the standalone light support changing \
                          hues (not yet tested)")

    parser.add_option_group(devicegroup)
    parser.add_option_group(fangroup)
    parser.add_option_group(addonlightgroup)
    parser.add_option_group(lightgroup)
    parser.add_option_group(wallcontrollergroup)
    opts, args = parser.parse_args()

    if not all([opts.ip, opts.name]):
        print('ip and the fan name are required')
        return 1
    else:
        fan = SenseMe(ip=opts.ip, name=opts.name, model=opts.model)

    #Process all the command line arguments

    #Device commands first
    if opts.get_beepersound:
        mode = fan.beepersound
        print(mode)
        return 0
    elif opts.set_beepersound:
        mode = (opts.set_beepersound).lower()
        if mode == "off" or mode =="on":
            fan.beepersound = mode
            return 0
        else:
            print ('Invalid beeper sound specified, valid option are \
                    off or on')
        return 1
    elif opts.get_devicetime:
        print(fan.devicetime)
        return 0
    elif opts.get_firmwarename:
        print(fan.firmwarename)
        return 0
    elif opts.get_firmwareversion:
        print(fan.firmwareversion)
        return 0
    elif opts.list_devices:
        devices = discover()
        for device in devices:
            print("%s,%s,%s,%s,\"%s\"" %
                  (device.name,device.ip,device.mac,device.series,device.model))
        return 0
    elif opts.get_ledindicators:
        mode = fan.led_indicators
        print(mode)
        return 0
    elif opts.set_ledindicators:
        mode = (opts.set_ledindicators).lower()
        if mode == "off" or mode =="on":
            fan.led_indicators = mode
            return 0
        else:
            print ("Invalid led indicator state specified, valid option are "
            "off or on")
            return 1
    elif opts.get_networkapstatus:
        print(fan.network_apstatus)
        return 0
    elif opts.get_networkdhcpstate:
        print(fan.network_dhcpstate)
        return 0
    elif opts.get_networkparameters:
        (ip,subnetmask,defaultgw) = fan.network_parameters
        print(ip + ',' + subnetmask + ',' + defaultgw)
        return 0
    elif opts.get_networkssid:
        print(fan.network_ssid)
        return 0
    elif opts.get_networktoken:
        print(fan.network_token)
        return 0

    #Fan commands
    elif opts.get_fanmode:
        mode = fan.fan_powered_on
        if mode == True:
            print('on')
        else:
            print('off')
        return 0
    elif opts.set_fanmode:
        mode = (opts.set_fanmode).lower()
        if mode ==  'on':
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
    elif opts.set_speed != None:
        if opts.set_speed >= 7:
            fan.speed = 7
        elif opts.set_speed <= 0:
            fan.speed = 0
        else:
            fan.speed = opts.set_speed
        return 0
    elif opts.get_minspeed:
        print(fan.minspeed)
        return 0
    elif opts.get_maxspeed:
        print(fan.maxspeed)
        return 0
    elif opts.get_roomfanspeedlimits:
        (min,max) = fan.roomsettings_fanspeedlimits
        print("%d %d" % (min,max))
    elif opts.roomfanspeedlimits:
        minspeed = opts.roomfanspeedlimits[0]
        maxspeed = opts.roomfanspeedlimits[1]
        fan.roomsettings_fanspeedlimits = (minspeed,maxspeed)
    elif opts.decrease_fanspeed:
        fan.dec_speed()
        return 0
    elif opts.increase_fanspeed:
        fan.inc_speed()
        return 0 
    elif opts.get_learnmode:
        mode = fan.learnmode
        print(mode.lower())
        return 0
    elif opts.set_learnmode:
        mode = (opts.set_learnmode).lower()
        if mode == "off" or mode =="on":
            fan.learnmode = mode
            return 0
        else:
            print ('Invalid learn mode specified, valid option are \
                    off or on')
            return 1
    elif opts.get_learnmodezerotemp:
        print(fan.learnmode_zerotemp)
        return 0
    elif opts.set_learnmodezerotemp:
        if opts.set_learnmodezerotemp >= 90:
            fan.learnmode_zerotemp = 90
        elif opts.set_learnmodezerotemp <= 50:
            fan.learnmode_zerotemp = 50
        else:
            fan.learnmode_zerotemp = opts.set_learnmodezerotemp
        return 0
    elif opts.get_learnmodeminspeed:
        print(fan.learnmode_minspeed)
        return 0
    elif opts.set_learnmodeminspeed != None:
        if opts.set_learnmodeminspeed >= 7:
            fan.learnmode_minspeed = 7
        elif opts.set_learnmodeminspeed <= 0:
            fan.learnmode_minspeed = 0
        else:
            fan.learnmode_minspeed = opts.set_learnmodeminspeed
        return 0
    elif opts.get_learnmodemaxspeed:
        print(fan.learnmode_maxspeed)
        return 0
    elif opts.set_learnmodemaxspeed != None:
        if opts.set_learnmodemaxspeed >= 7:
            fan.learnmode_maxspeed = 7
        elif opts.set_learnmodemaxspeed <= 0:
            fan.learnmode_maxspeed = 0
        else:
            fan.learnmode_maxspeed = opts.set_learnmodemaxspeed
        return 0
    elif opts.get_smartsleepmode:
        mode = fan.smartsleepmode
        print(mode.lower())
        return 0
    elif opts.set_smartsleepmode:
        mode = (opts.set_smartsleepmode).lower()
        if mode == "off" or mode =="on":
            fan.smartsleep_mode = mode
            return 0
        else:
            print ('Invalid smartsleep mode specified, valid option are \
                    off or on')
            return 1
    elif opts.get_smartsleepidealtemp:
        print(fan.smartsleep_idealtemp)
        return 0
    elif opts.set_smartsleepidealtemp:
        if opts.set_smartsleepidealtemp >= 90:
            fan.smartsleep_idealtemp = 90
        elif opts.set_smartsleepidealtemp <= 50:
            fan.smartsleep_idealtemp = 50
        else:
            fan.smartsleep_idealtemp = opts.set_smartsleepidealtemp
        return 0
    elif opts.get_smartsleepminspeed:
        print(fan.smartsleep_minspeed)
        return 0
    elif opts.set_smartsleepminspeed != None:
        if opts.set_smartsleepminspeed >= 7:
            fan.smartsleep_minspeed = 7
        elif opts.set_smartsleepminspeed <= 0:
            fan.smartsleep_minspeed = 0
        else:
            fan.smartsleep_minspeed = opts.set_smartsleepminspeed
        return 0
    elif opts.get_smartsleepmaxspeed:
        print(fan.smartsleep_maxspeed)
        return 0
    elif opts.set_smartsleepmaxspeed != None:
        if opts.set_smartsleepmaxspeed >= 7:
            fan.smartsleep_maxspeed = 7
        elif opts.set_smartsleepmaxspeed <= 0:
            fan.smartsleep_maxspeed = 0
        else:
            fan.smartsleep_maxspeed = opts.set_smartsleepmaxspeed
        return 0
    elif opts.get_smartsleepwakeupbrightness:
        print(fan.smartsleep_wakeupbrightness)
        return 0
    elif opts.set_smartsleepwakeupbrightness != None:
        if opts.set_smartsleepwakeupbrightness >= 16:
            fan.smartsleep_wakeupbrightness = 16
        elif opts.set_smartsleepwakeupbrightness <= 0:
            fan.smartsleep_wakeupbrightness = 0
        else:
            fan.smartsleep_wakeupbrightness = \
            opts.set_smartsleepwakeupbrightness
        return 0
    elif opts.get_fandirection:
        mode = fan.fandirection
        if mode == "fwd":
            print('forward')
        else:
            print('reverse')
        return 0
    elif opts.set_fandirection:
        mode = (opts.set_fandirection).lower()
        if mode == "forward":
            fan.fandirection = 'FWD'
            return 0
        elif mode =="reverse":
            fan.fandirection = 'REV'
            return 0
        else:
            print ('Invalid fan direction specified, valid option are \
                    forward or reverse')
            return 1 
    elif opts.get_fanmotionmode:
        mode = fan.fan_motionmode
        print(mode.lower())
        return 0
    elif opts.set_fanmotionmode:
        mode = (opts.set_fanmotionmode).lower()
        if mode == "off" or mode =="on":
            fan.fan_motionmode = mode
            return 0
        else:
            print ('Invalid fan motion detection mode specified, valid option are \
                    off or on')
            return 1
    elif opts.get_motionmodemintimer:
        print(fan.motionmode_mintimer)
        return 0
    elif opts.get_motionmodemaxtimer:
        print(fan.motionmode_maxtimer)
        return 0
    elif opts.get_motionmodecurrenttimer:
        print(fan.motionmode_currenttimer)
        return 0
    elif opts.get_motionmodeoccupiedstatus:
        mode = fan.motionmode_occupiedstatus
        print(mode.lower())
        return 0
    elif opts.get_wintermode:
        mode = fan.wintermode
        print(mode)
        return 0
    elif opts.set_wintermode:
        mode = (opts.set_wintermode).lower()
        if mode == "off" or mode =="on":
            fan.wintermode = mode
            return 0
        else:
            print ('Invalid winter mode specified, valid option are \
                    off or on')
        return 1
    elif opts.get_smartmode:
        mode = fan.smartmode
        print(mode)
        return 0
    elif opts.set_smartmode:
        mode = (opts.set_smartmode).lower()
        if mode == "off" or mode =="cooling" or mode == "heating":
            fan.smartmode = mode
            return 0
        else:
            print ('Invalid smart mode specified, valid option are \
                    off, cooling or heating')
        return 1
    elif opts.get_whooshmode:
        mode = fan.whoosh
        if mode == True:
            print('on')
        else:
            print('off')
        return 0
    elif opts.set_whooshmode:
        mode = (opts.set_whooshmode).lower()
        if mode ==  'on':
            fan.whoosh = True
        else:
            fan.whoosh = False
        return 0

    #Add-on Light Commands
    elif opts.get_brightness:
        print(fan.brightness)
        return 0
    elif opts.set_brightness != None:
        if opts.set_brightness >= 16:
            fan.brightness = 16
        elif opts.set_brightness <= 0:
            fan.brightness = 0
        else:
            fan.brightness = opts.set_brightness
        return 0
    elif opts.get_minbrightness:
        print(fan.minbrightness)
        return 0
    elif opts.get_maxbrightness:
        print(fan.maxbrightness)
        return 0
    elif opts.get_roombrightnesslimits:
        (min,max) = fan.roomsettings_brightnesslimits
        print("%d %d" % (min,max))
        return 0
    elif opts.roombrightnesslimits:
        minbrightness = opts.roombrightnesslimits[0]
        maxbrightness = opts.roombrightnesslimits[1]
        fan.roomsettings_brightnesslimits = (minbrightness,maxbrightness)
        return 0
    elif opts.decrease_brightness:
        fan.dec_brightness()
        return 0
    elif opts.increase_brightness:
        fan.inc_brightness()
        return 0
    elif opts.isfanlightinstalled:
        mode = fan.isfanlightinstalled
        if mode == True:
            print("installed")
            return 1
        else:
            print('not installed')
        return 0
    elif opts.get_lightmotionmode:
        mode = fan.light_motionmode
        print(mode.lower())
        return 0
    elif opts.set_lightmotionmode:
        mode = (opts.set_lightmotionmode).lower()
        if mode == "off" or mode =="on":
            fan.light_motionmode = mode
            return 0
        else:
            print ('Invalid light motion detection mode specified, valid option are \
                    off or on')
            return 1
    elif opts.get_lightmode:
        mode = fan.light_powered_on
        if mode == True:
            print('on')
        else:
            print('off')
        return 0
    elif opts.set_lightmode:
        mode = (opts.set_lightmode).lower()
        if mode ==  'on':
            fan.light_powered_on = True
        else:
            fan.light_powered_on = False
        return 0
    elif opts.toggle_lightmode:
        fan.light_toggle()
        return 0

     #standalone light commands
    elif opts.get_lighthue:
        print(fan.light_hue)
        return 0
    elif opts.set_lighthue != None:
        if opts.set_lighthue >= 5000:
            fan.light_hue= 5000 
        elif opts.set_lighthue<= 2200:
            fan.light_hue = 2200
        else:
            fan.light_hue = opts.set_lighthue
        return 0
    elif opts.islightcolor:
        mode = fan.islightcolor
        if mode == True:
            print("color")
            return 1
        else:
            print('not color')
        return 0
    else:
        print('Invalid argument specified')
        return 1


if __name__ == "__main__":
    main()
