import socket

import netifaces

from tornado.ioloop import IOLoop
from tornado.tcpserver import TCPServer
from zeroconf import ServiceInfo

from connection.base_service import BaseService
from connection.settings import SERVICE_TYPE_NAME, PORT


class FileGetTCPServer(TCPServer):
    def handle_stream(self, stream, address):
        stream.read_bytes(16384, callback=self.on_read_done)

    @staticmethod
    def on_read_done(data):
        filename = "1234.mp4"  # TODO Send filename later
        with open(filename, "ab") as f:
            f.write(data)
        # IOLoop.current().stop()


class Server(BaseService):
    """ Waiting files. """

    def __init__(self, identifier):
        super(Server, self).__init__(identifier)
        desc = {'path': None}
        interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        IP = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        info = ServiceInfo(
            SERVICE_TYPE_NAME,
            "%s.%s" % (identifier, SERVICE_TYPE_NAME),
            socket.inet_aton(IP),
            PORT,
            0,
            0,
            desc,
            None
        )
        self.zero_conf.register_service(info)
        print("Service '%s' registered." % info.name)
        server = FileGetTCPServer()
        server.listen(PORT)
        try:
            IOLoop.current().start()
        except KeyboardInterrupt:
            pass
        finally:
            print("Unregistering service: %s" % info.name)
            self.zero_conf.unregister_service(info)
            self.zero_conf.close()
            server.stop()
