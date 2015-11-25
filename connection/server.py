import socket
import netifaces
from progressbar import ProgressBar
from zeroconf import ServiceInfo
from connection.base_service import BaseService
from connection.settings import SERVICE_TYPE_NAME, PORT, CHUNK_MAX_SIZE


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
        sock = socket.socket()
        sock.bind((IP, PORT))
        sock.listen(1)
        try:
            connection, client_address = sock.accept()
            print('Get file from', client_address[0])
            file_name = "123123.mp4"  # TODO Send filename later
            file = open(file_name, "wb")
            file_size = self._get_file_size(connection)
            total_receive_bytes_count = 0
            bar = ProgressBar(maxval=100).start()
            while True:
                data = connection.recv(CHUNK_MAX_SIZE)
                receive_bytes_count = len(data)
                total_receive_bytes_count += receive_bytes_count
                if len(data) == 0:
                    break
                bar.update(round((total_receive_bytes_count / file_size * 100), 2))
                file.write(data)
            file.close()
            print("\nReceiving done.")
            connection.close()
        except KeyboardInterrupt:
            pass
        finally:
            print("Unregistering service: %s." % info.name)
            self.zero_conf.unregister_service(info)
            self.zero_conf.close()

    @staticmethod
    def _get_file_size(connection):
        data = None
        while True:
            data = connection.recv(4)
            if len(data) == 4:
                break
        return int(data.hex(), 16)

    def _get_file_name(self, connection):
        pass
