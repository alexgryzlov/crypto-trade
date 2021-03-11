import typing as tp


class Signal:
    def __init__(self, name: str, content: tp.Any):
        self.name = name
        self.content = content

    def __repr__(self) -> str:
        return f'Signal {self.name}: {self.content}'
