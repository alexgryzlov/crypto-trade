import typing as tp

Any = tp.TypeVar('Any')


def require(var: tp.Optional[Any]) -> Any:
    if var is None:
        raise ValueError('variable hasn\'t been set')
    return var
