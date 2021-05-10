import math

def ceil(x: float, n: int) -> float:
    return math.floor(x * 10 ** n) / 10 ** n
