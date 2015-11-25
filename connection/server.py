import socket
import netifaces
from progressbar import ProgressBar
from zeroconf import ServiceInfo
from connection.base_service import BaseService
from connection.settings import *


class Server(BaseService):
    """ Waiting files. """

    def __init__(self, identifier):
        super(Server, self).__init__(identifier)
        desc = {'path': None}
        interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        ip_address = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        info = ServiceInfo(
            SERVICE_TYPE_NAME,
            "%s.%s" % (identifier, SERVICE_TYPE_NAME),
            socket.inet_aton(ip_address),
            PORT,
            0,
            0,
            desc,
            None
        )
        self.zero_conf.register_service(info)
        print("Service '%s' registered." % info.name)
        sock = socket.socket()
        sock.bind((ip_address, PORT))
        sock.listen(1)
        try:
            connection, client_address = sock.accept()
            print('Get file from', client_address[0])
            file_name_size = self._get_size(connection, FILE_NAME_SIZE_BYTES_COUNT)
            file_name = self._get_file_name(connection, file_name_size)
            file = open(file_name, "wb")
            file_size = self._get_size(connection, FILE_SIZE_BYTES_COUNT)
            total_receive_bytes_count = 0
            bar = ProgressBar(maxval=100).start()
            while True:
                data = connection.recv(CHUNK_MAX_SIZE)
                receive_bytes_count = len(data)
                total_receive_bytes_count += receive_bytes_count
                if len(data) == 0:
                    break
                bar.update(total_receive_bytes_count / file_size * 100)
                file.write(data)
            print("\nReceiving done.")
        except KeyboardInterrupt:
            pass
        finally:
            print("Unregistering service: %s." % info.name)
            self.zero_conf.unregister_service(info)
            self.zero_conf.close()

    @staticmethod
    def _get_size(connection, bytes_read_count):
        data = None
        while True:
            data = connection.recv(bytes_read_count)
            if len(data) == bytes_read_count:
                break
        return int.from_bytes(data, 'big')

    @staticmethod
    def _get_file_name(connection, file_name_size):
        data = None
        while True:
            data = connection.recv(file_name_size)
            if len(data) == file_name_size:
                break
        return data.decode('utf-8')
