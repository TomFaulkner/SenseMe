from senseme.senseme import decode_discovery


def test_discovery_message_decoding():
    test_message = ("(NAME;DEVICE;ID;MAC;MODEL,SERIES)".encode("utf-8"), ("127.0.0.1", "3101"))
    name, mac, model, series, ip = decode_discovery(test_message)
    assert ("NAME", "MAC", "MODEL", "SERIES", "127.0.0.1") == (name, mac, model, series, ip)
