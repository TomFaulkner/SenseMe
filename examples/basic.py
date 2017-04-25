from senseme import discover


def main():
    # discover devices, returns list of SenseMe devices
    devices = discover()
    fan = devices[0]

    # Statically assign the fan? Probably not, but you would do it this way:
    # from senseme import SenseMe
    # fan = SenseMe('192.168.1.50', 'Living Room Fan', model='FAN')
    # fan = SenseMe(name="Living Room Fan")

    # Turn the light off / on
    # fan.light_powered_on = False
    # fan.light_powered_on = True
    # light_status = fan.light_toggle()

    # Increase light level by 2 levels
    # fan.inc_brightness(2)

    # Get Light level
    # print(fan.brightness)

    # Fan Speeds
    # fan.fan_powered_on = True
    # fan.fan_powered_on = False
    # print(fan.speed)
    # fan.speed = 5

    # whoosh mode
    # fan.whoosh = True

    # want an increasing light effect? Do this.
    # But, really, probably don't, I don't think Haiku intended strobe effects.
    # I'm not responsible if you make a strobe light and break the fan or worse
    # for intensity in range(1,16):
    #   fan.brightness = intensity
    #   time.sleep(1)

    # export details to json / xml / str(dict)
    # fan.json
    # fan.xml
    # fan.dict  # nested dict
    # fan.flat_dict  # flattened

    # Listen for broadcasts, useful for debugging,
    # wouldn't suggest using it for anything else
    # fan.listen()


main()
