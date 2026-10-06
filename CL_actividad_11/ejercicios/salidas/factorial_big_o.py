def factorial(n):  # funcion factorial: O(n)
    if n < 0:  # O(1)
        return None  # O(1)
    resultado = 1  # O(1)
    for i in range(2, n + 1):  # O(n)
        resultado *= i  # O(1) x O(n) = O(n)
    return resultado  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion factorial
#   Suma de complejidades individuales:
#     O(1) + O(1) + O(1) + O(n) + O(n) + O(1)
#     = 2n + 4
#   Complejidad de mayor grado: O(n)
# ==========================================================================
