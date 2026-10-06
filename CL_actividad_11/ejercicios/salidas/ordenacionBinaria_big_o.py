def ordenacionBinaria(lista, objetivo):  # funcion ordenacionBinaria: O(log n)
    izquierda, derecha = 0, len(lista) - 1  # O(1)
    while izquierda <= derecha:  # O(log n)  (la variable de control se divide o multiplica en cada vuelta)
        medio = (izquierda + derecha) // 2  # O(1) x O(log n) = O(log n)
        if lista[medio] == objetivo:  # O(1) x O(log n) = O(log n)
            return medio  # O(1) x O(log n) = O(log n)
        elif lista[medio] < objetivo:  # O(1) x O(log n) = O(log n)
            izquierda = medio + 1  # O(1) x O(log n) = O(log n)
        else:
            derecha = medio - 1  # O(1) x O(log n) = O(log n)
    return -1  # O(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- PEOR CASO (Big-O)
# ==========================================================================
# Funcion ordenacionBinaria
#   Suma de complejidades individuales:
#     O(1) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n) + O(log n)
#     + O(log n) + O(1)
#     = 7 log n + 2
#   Complejidad de mayor grado: O(log n)
# ==========================================================================
