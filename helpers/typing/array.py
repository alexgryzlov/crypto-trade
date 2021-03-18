import typing as tp
import numpy as np

_Scalar = tp.TypeVar('_Scalar', covariant=True)

Array = tp.Union[tp.Sequence[_Scalar], np.ndarray]
