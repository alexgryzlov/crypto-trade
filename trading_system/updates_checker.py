import functools
import typing as tp

from collections.abc import Callable, Iterable
from collections import defaultdict

from trading_system.trading_system_handler import TradingSystemHandler


class FromClass:
    """ Helper for getting dependencies from class object. """

    def __init__(self, getter: tp.Callable[[tp.Any], tp.Iterable[str]]) -> None:
        """
            @param getter Function for getting dependencies from class object
        """
        self.getter = getter

    def get(self, cls: tp.Any) -> tp.Union[tp.Iterable[str]]:
        return self.getter(cls)


def handlers_name(handler: TradingSystemHandler) -> str:
    """ check_update helper for handlers """
    return handler.get_name()


class UpdatesChecker:
    """ Tracking updates of functions and executing if dependencies updated.
        Example:
            @check_update('unique name')
            def update():
                x += 1
                return True

            @on_updates(['unique name'], None)
            def check():
                return x
    """
    last_updates = defaultdict(int)  # type: ignore
    last_executed = defaultdict(lambda: defaultdict(int))  # type: ignore

    @staticmethod
    def check_update(name: tp.Optional[tp.Union[str, tp.Callable[[tp.Any], str]]] = None,
                     updated: tp.Callable[[tp.Any], bool] = lambda x: x) -> tp.Any:
        """ Decorator for tracking updates of some function
            @param name Unique name to track updates (or Callable of self param of a method)
            @param updated Callable on result of function to determine if function updated something
        """

        def inner(func: tp.Callable[[tp.Any], tp.Any]) -> tp.Callable[[tp.Any], tp.Any]:
            _name = name
            if _name is None:
                _name = str(func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):  # type: ignore
                nonlocal _name
                if isinstance(_name, Callable):
                    _name = _name(args[0])
                result = func(*args, **kwargs)
                if updated(result):
                    UpdatesChecker.last_updates[_name] += 1
                return result

            return wrapper

        return inner

    @staticmethod
    def on_updates(of: tp.Union[FromClass, tp.Iterable[str]], default: tp.Any,
                   updated: str = 'all') -> tp.Any:
        """ Decorator for executing if all or any dependencies updated.
            @param of Unique names to track (or Callable of self param of method)
            @param default Return value if dependencies were not updated
            @param updated Execute if 'all' or 'any' dependencies updated
        """

        def inner(func: tp.Callable[[tp.Any], tp.Any]) -> tp.Callable[[tp.Any], tp.Any]:
            if '_of' not in locals():
                _of = of

            @functools.wraps(func)
            def wrapper(*args, **kwargs):  # type: ignore
                nonlocal _of
                if isinstance(_of, FromClass):
                    _of = _of.get(args[0])

                updated_dependencies = [UpdatesChecker.last_updates[dependency] >
                                        UpdatesChecker.last_executed[str(func)][dependency]
                                        for dependency in _of]
                if (updated == 'all' and not all(updated_dependencies)) or \
                        (updated == 'any' and not any(updated_dependencies)):
                    return default

                result = func(*args, **kwargs)
                for dependency in _of:
                    UpdatesChecker.last_executed[str(func)][dependency] = UpdatesChecker.last_updates[dependency]
                return result

            return wrapper

        return inner
