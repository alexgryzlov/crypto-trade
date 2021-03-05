class Signal:
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __repr__(self):
        return f'Signal {self.name}: {self.content}'
