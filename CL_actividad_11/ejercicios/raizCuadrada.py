def raizCuadrada(n):
    if n < 0:
        return None
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x
