def burbuja(lista):  # funcion burbuja: O(n^2)
    n = len(lista)  # O(1)
    for i in range(n):  # O(n)
        for j in range(0, n - i - 1):  # O(n) x O(n) = O(n^2)
            if lista[j] > lista[j + 1]:  # O(1) x O(n^2) = O(n^2)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # O(1) x O(n^2) = O(n^2)
    return lista  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion burbuja
#   Suma de complejidades individuales:
#     O(1) + O(n) + O(n^2) + O(n^2) + O(n^2) + O(1)
#     = 3n^2 + n + 2
#   Complejidad de mayor grado: O(n^2)
# ==========================================================================
