def raizCuadrada(n):  # funcion raizCuadrada: O(log n)
    if n < 0:  # O(1)
        return None  # O(1)
    x = n  # O(1)
    y = (x + 1) // 2  # O(1)
    while y < x:  # O(log n)  (la variable de control se divide o multiplica en cada vuelta)
        x = y  # O(1) x O(log n) = O(log n)
        y = (x + n // x) // 2  # O(1) x O(log n) = O(log n)
    return x  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion raizCuadrada
#   Suma de complejidades individuales:
#     O(1) + O(1) + O(1) + O(1) + O(log n) + O(log n) + O(log n) + O(1)
#     = 3 log n + 5
#   Complejidad de mayor grado: O(log n)
# ==========================================================================
