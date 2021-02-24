import pickle


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args,
                                                                 **kwargs)
        return cls._instances[cls]


class ObjectLog(metaclass=Singleton):
    def __init__(self):
        self.log = []

    def add_event(self, event):
        self.log.append(event)

    def store_log(self, filename='object_log.dump'):
        with open(filename, 'wb') as f:
            pickle.dump(self.log, f)
