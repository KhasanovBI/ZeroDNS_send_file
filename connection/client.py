import socket

from tornado.ioloop import IOLoop
from tornado.iostream import IOStream

from connection.base_service import BaseService
from connection.settings import SERVICE_TYPE_NAME, SERVICE_SEARCH_TIMEOUT


class Client(BaseService):
    def __init__(self, identifier):
        super(Client, self).__init__(identifier)
        self.service_full_identifier = "%s.%s" % (self.identifier, SERVICE_TYPE_NAME)
        self.service_info = self.zero_conf.get_service_info(SERVICE_TYPE_NAME,
                                                            self.service_full_identifier,
                                                            SERVICE_SEARCH_TIMEOUT)
        if self.service_info:
            self.server_IP = socket.inet_ntoa(self.service_info.address)
            self.server_port = self.service_info.port
            print("Find service %s(%s:%d)." % (self.service_info.server, self.server_IP, self.server_port))
        else:
            raise ConnectionError("Can't find service")

    def send_file(self, filename):
        def send_request():
            with open(filename, "rb") as f:
                self.stream.write(f.read())
            IOLoop.current().stop()

        print("Send %s" % filename)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = IOStream(s)
        self.stream.connect((self.server_IP, self.server_port), send_request)
        IOLoop.current().start()
