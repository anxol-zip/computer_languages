def burbuja(lista):  # funcion burbuja: Ω(n^2)
    n = len(lista)  # Ω(1)
    for i in range(n):  # Ω(n)
        for j in range(0, n - i - 1):  # Ω(n) x Ω(n) = Ω(n^2)
            if lista[j] > lista[j + 1]:  # Ω(1) x Ω(n^2) = Ω(n^2)
                lista[j], lista[j + 1] = lista[j + 1], lista[j]  # Ω(1) x Ω(n^2) = Ω(n^2)  (rama no ejecutada en el mejor caso)
    return lista  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion burbuja
#   Suma de complejidades individuales:
#     Ω(1) + Ω(n) + Ω(n^2) + Ω(n^2) + Ω(1)
#     = 2n^2 + n + 2
#   Complejidad de mayor grado: Ω(n^2)
# ==========================================================================
