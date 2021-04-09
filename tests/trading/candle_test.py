from numpy.random import random

from trading import Candle


def test_hash_and_eq() -> None:
    for i in range(1000):
        vals = sorted(random(4))
        candle = Candle(i, vals[1], vals[2], vals[0], vals[3], 1)
        same_candle = Candle(i, vals[1], vals[2], vals[0], vals[3], 1)
        other_candle = Candle(i, vals[2], vals[1], vals[0], vals[3], 1)
        assert (candle == same_candle)
        assert (hash(candle) == hash(same_candle))
        assert (candle != other_candle)
