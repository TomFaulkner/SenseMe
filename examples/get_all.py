""" Get all config data from all devices """
from senseme import discover


def discover_and_getall():
    print("Discovering...")
    devices = discover()
    print("Discovered:")
    for device in devices:
        print(device, "\n", repr(device))

    for device in devices:
        results = device.send_raw("<%s;GETALL>" % device.name)
        print(len(results), "result strings.")
        for result in results:
            print(result)


if __name__ == "__main__":
    discover_and_getall()
