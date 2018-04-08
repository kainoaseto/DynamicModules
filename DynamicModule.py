from abc import ABCMeta, abstractmethod


class DynamicModule(metaclass=ABCMeta):
    def __init__(self):
        print("DynamicModule")
        #super().__init__()

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def shutdown(self):
        pass

