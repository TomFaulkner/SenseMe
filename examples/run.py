from senseme.senseme import SenseMe


def main():
    # Statically assign the fan? Probably not, but you would do it this way:
    # fan = senseme('192.168.1.50', 'Living Room Fan', model='FAN')
    # fan = senseme(name="Living Room Fan")
    fan = SenseMe()

    # Turn the light off
    # fan.lightoff()

    # Get Light level
    # light = fan.getlight()
    # print(light)

    # Get fan speed
    # motor = fan.getfan()
    # print(motor)

    # Toggle light status
    fan.light_toggle()

    # want an increasing light effect? Do this.
    # But, really, probably don't, I don't think they intended strobe effects.
    # I'm not responsible if you make a strobe light and break the fan or worse
    # for intensity in range(1,16):
    #   fan.setlight(intensity)
    #   time.sleep(1)

    # Increase light level by 2 levels
    # fan.inclight(2)

    # Listen for broadcasts, useful for debugging,
    # wouldn't suggest using it for anything else
    # fan.listen()


main()
