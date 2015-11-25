from zeroconf import Zeroconf


class BaseService(object):
    def __init__(self, identifier):
        self.identifier = identifier
        self.zero_conf = Zeroconf()
