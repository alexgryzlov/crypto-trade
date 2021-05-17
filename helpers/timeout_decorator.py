import functools
import signal
import typing as tp
from helpers.typing.method import Method


def raise_timeout_exception() -> tp.NoReturn:
    raise TimeoutError


def timeout(
        seconds: int,
        handler: Method = raise_timeout_exception
        ) -> tp.Callable[[Method], Method]:
    def timeout_impl(func: Method) -> Method:
        @functools.wraps(func)
        def wrapper(*args: tp.Any, **kwargs: tp.Any) -> None:
            signal.signal(signal.SIGALRM, lambda signum, frame: handler())
            signal.alarm(seconds)
            func(*args, **kwargs)
        return wrapper
    return timeout_impl
