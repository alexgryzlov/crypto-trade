import os


class _Getch:
    def __init__(self) -> None:
        if os.name == 'nt':
            self.getch = _Getch.__getch_windows
        else:
            self.getch = _Getch.__getch_unix

    @staticmethod
    def __getch_unix() -> str:
        import sys
        import tty
        import termios

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    @staticmethod
    def __getch_windows() -> str:
        import msvcrt

        return msvcrt.getch()  # type: ignore


getch = _Getch().getch
