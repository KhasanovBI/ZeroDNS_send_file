import os
import socket

from progressbar import ProgressBar

from connection.base_service import BaseService
from connection.settings import *


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

    @staticmethod
    def _send_bytes(sock, message):
        total_sent_bytes_count = 0
        while total_sent_bytes_count < len(message):
            sent_bytes_count = sock.send(message[total_sent_bytes_count:])
            if sent_bytes_count == 0:
                raise RuntimeError("Connection error")
            total_sent_bytes_count += sent_bytes_count

    def send_file(self, file_name):
        print("Send %s" % file_name)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        sock.connect((self.server_IP, self.server_port))
        file_size = os.stat(file_name).st_size
        binary_file_name = file_name.encode("utf-8")
        self._send_bytes(sock, len(binary_file_name).to_bytes(FILE_NAME_SIZE_BYTES_COUNT, 'big'))
        self._send_bytes(sock, binary_file_name)
        self._send_bytes(sock, file_size.to_bytes(FILE_SIZE_BYTES_COUNT, 'big'))
        bar = ProgressBar(maxval=100).start()
        total_sent_bytes_count = 0
        with open(file_name, "rb") as f:
            while True:
                chunk = f.read(CHUNK_MAX_SIZE)
                if not chunk:
                    break
                chunk_size = len(chunk)
                self._send_bytes(sock, chunk)
                total_sent_bytes_count += chunk_size
                bar.update(total_sent_bytes_count / file_size * 100)
        self.zero_conf.close()
