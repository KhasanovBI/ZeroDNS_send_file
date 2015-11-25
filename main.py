import sys

from connection.client import Client
from connection.server import Server


def main():
    args_count = len(sys.argv)
    if args_count == 2:
        server = Server(sys.argv[1])
    elif args_count > 2:
        client = Client(sys.argv[1])
        for i in range(2, args_count):
            client.send_file(sys.argv[i])


if __name__ == '__main__':
    main()
