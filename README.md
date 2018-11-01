[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# SenseMe
Python Library for Haiku SenseMe app controlled fans/lights

This library is useful to control Haiku SenseMe fans with light kits. I would expect it will probably also work with their lights.

It might also be useful for controlling DIY projects as the protocol is very simple and would be easy to clone. And, if you were to use their API the Android and iOS apps may work to control DIY devices. A suggested idea would be to add an Arduino or Raspberry Pi and a relay or two to your own fan and use this or the Haiku Home app to control them. I've read that doing this sort of thing [with a resistor is a dangerous idea, so don't do that.](https://arstechnica.com/civis/viewtopic.php?t=1263401)

Sniffing the packets and documenting the protocol were the work of [Bruce](http://bruce.pennypacker.org/tag/senseme-plugin/). Much of the code was based on his work on making [an Indigo plugin](https://github.com/bpennypacker/SenseME-Indigo-Plugin)

See [Issues](issues) for known issues or if you want to contribute but don't know where to start. Some easy fixes are labeled.

I am not affiliated with Haiku Home or Big Ass Fans. Their support rep said this project seemed cool in it's infancy, and they even answered a technical question regarding the protocol for me, so hopefully they still approve.

# Future
Some ideas for future related projects and features:

 1. Plex plugin (dim the fans when the movie starts and light up when it is paused or ends? Yes, please!)

 2. Alexa / Google Home plugins (see REST API below)

 3. Store information in a database (sqlite, or even json, would be fine) rather than discovering each time.

 4. Track usage and temperatures

 5. Other automation system plugins

 6. REST API backend with a CLI client (a basic direct to fan command line client was added in 0.1.3)

 7. React or other web based client for the above API

 8. Docker image for the above

 9. Use protocol to control other devices by attaching an Arduino or Pi

 10. ~~Discover the rest of the protocol. (Run strings on the apps and some packet sniffing.)~~

 11. More examples

 12. ~~Command Line Client~~ Basic client added in 0.1.3, see [SenseMe CLI](#cli) below
 
 13. Unit Tests


# Usage
    from senseme import discover
    # discover devices, returns list of SenseMe devices
    devices = discover()
    fan = devices[0]
    repr(fan)

SenseMe(name='Living Room Fan', ip='192.168.1.50', model='FAN,HAIKU', series='HSERIES', mac='20:F8:5E:E3:AB:00')


    # Statically assign the fan? Probably not, but you would do it this way:
    from senseme import SenseMe
    fan = SenseMe('192.168.1.50', 'Living Room Fan', model='FAN')
    # or, this might be easier
    fan = SenseMe(name="Living Room Fan")

Control the fan:

    # Turn the light off / on
    fan.light_powered_on = False
    fan.light_powered_on = True
    # or, if you just want to toggle it
    light_status = fan.light_toggle()

    # Increase light level by 2 levels
    fan.inc_brightness(2)

    # Get Light level
    print(fan.brightness)

    # Fan Speeds
    fan.fan_powered_on = True
    fan.fan_powered_on = False
    print(fan.speed)

    # whoosh mode
    fan.whoosh = True

    # want an increasing light effect? Do this.
    # But, really, probably don't, I don't think Haiku intended strobe effects.
    # I'm not responsible if you make a strobe light and break the fan or worse
    for intensity in range(1,16):
        fan.brightness = intensity
        time.sleep(1)

    # export details to json / xml / str (as `str(dict)`)
    fan.json
    fan.xml
    fan.dict  # nested dict
    fan.flat_dict  # flattened

    # Listen for broadcasts, useful for debugging,
    # wouldn't suggest using it for anything else
    fan.listen()

# SenseMe CLI <a id="cli"></a>
In version 0.1.3 a script was added to control HaikuHome SenseMe devices from a command line.

Set the following environment variables:

    SENSEME_DEFAULT_FAN_IP
    SENSEME_DEFAULT_FAN_NAME

Then run `senseme_cli` with one of the following options.

    fan x           - set speed to x (0-7)
    fan on|off      - fan on/off
    light x         - set light brightness to x
    light on|off    - light on/off
    whoosh [on|off] - whoosh mode on/off

# Requirements
Python 3.6 is required to use this library.
SenseMe devices communicate on UDP port 31415 using broadcast and unicast traffic. Any firewall will have to allow this through.

