from abc import ABCMeta, abstractmethod

class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError

    @abstractmethod
    def plot(self):
        raise NotImplementedError
