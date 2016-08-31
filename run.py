import time

from sensemefan import SenseMeFan

# TODO: Function to broadcast the <ALL;DEVICE;ID;GET> command to find the fan
# TODO: Get IP from the above, since it isn't in the response
# TODO: Fix fan_listen to actually listen for broadcasts

def main():
    # fan = SenseMeFan('192.168.1.112', 'Living Room Fan')
    fan = SenseMeFan()

    # fan.lightoff()
    # light = fan.getlight()
    # print(light)

    # motor = fan.getfan()
    # print(motor)

    # fan.lighttoggle()

    # for intensity in range(1,16):
    #   fan.setlight(intensity)
    #   time.sleep(1)

    # fan.inclight(2)

    # findfan()

    # print(fan.__query__('<ALL;DEVICE;ID;GET>'))

    # fan.listen()

    # print(fan.fan_listen())
    return

main()