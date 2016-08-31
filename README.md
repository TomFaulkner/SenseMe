# SenseMe
Python Library for Haiku SenseMe app controlled fans/lights

This library is useful to control Haiku SenseMe fans with light kits. I would expect it will probably also work with their lights.

It might also be useful for controlling DIY projects as the protocol is very simple and would be easy to clone. And, if you were to use their API the Android and iOS apps may work to control DIY devices. A suggested idea would be to add an Arduino or Raspberry Pi and a relay or two to your own fan and use this or the Haiku Home app to control them.

Sample usage is found in run.py

Going forward, I expect to work this in with Flask to put on a VM to control the fan from a webpage on my phone or desktop. (Unfortunately, their app doesn't seem to broadcast properly so it doesn't work on my Nexus 6P. This issue is what lead to this project.)

Sniffing the packets and documenting the protocol were the work of Bruce at http://bruce.pennypacker.org/tag/senseme-plugin/. Much of the code was based on his work on making an Indigo plugin for this fan: https://github.com/bpennypacker/SenseME-Indigo-Plugin

I'm new to Python, so there are probably poor coding standards in places, I'm sorry for that.

## Usage
  
  from sensemefan import SenseMeFan
  def main():
    # Statically assign the fan? Probably not, but you would do it this way.
    # fan = SenseMeFan('192.168.1.112', 'Living Room Fan')
    
    # Create the fan object and discover the fan
    fan = SenseMeFan()

    # Turn the light off
    # fan.lightoff()
    
    # Get the light level
    # light = fan.getlight()
    # print(light)

    # Get the fan speed
    # motor = fan.getfan()
    # print(motor)

    # Toggle fan motor on/off
    # fan.lighttoggle()

    # want an increasing light effect? Do this.
    # But, really, probably don't, I don't think they intended strobe effects.
    # I'm not responsible if you make a strobe light and break the fan or worse
    # for intensity in range(1,16):
    #   fan.setlight(intensity)
    #   time.sleep(1)

    # increase the light level by 2 levels
    # fan.inclight(2)

    # listen for broadcasts, useful for debugging, wouldn't suggest using it for anything else
    # fan.listen()

    return

main()
