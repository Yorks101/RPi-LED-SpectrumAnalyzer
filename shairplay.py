from struct import pack
from Shairplay import DnssdService, LoadShairplay, RaopLogLevel, RaopService

SERVICES = {}

def get_port(port=5000):
    import socket
    s = socket.socket()
    while True:
        try:
            s.bind(('', port))
            return port
        except socket.error:
            port += 1

def initialize_shairplay(path, callback_class, log_callback=None):
    """ Initialize shairplay and return the services created. """

    if not callable(log_callback):
        def log_callback(level, message):
            pass

    shairplay = LoadShairplay(path)
    callbacks = callback_class()

    raop = RaopService(shairplay, 10, callbacks)
    raop.set_log_level(RaopLogLevel.DEBUG)
    raop.set_log_callback(log_callback)

    raop = RaopService(shairplay, 10, callbacks)
    raop.set_log_level(RaopLogLevel.DEBUG)
    raop.set_log_callback(log_callback)

    hwaddr = pack('BBBBBB', 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB)
    port = get_port()
    port = raop.start(port, hwaddr)

    dnssd = DnssdService(shairplay)
    dnssd.register_raop("Pi-Rainbow", port, hwaddr)

    SERVICES['raop'] = raop
    SERVICES['dnssd'] = dnssd

    return


def shutdown_shairplay():
    if 'raop' in SERVICES:
        SERVICES['raop'].stop()
        del SERVICES['raop']

    if 'dnssd' in SERVICES:
        SERVICES['dnssd'].unregister_raop()
        del SERVICES['dnssd']
