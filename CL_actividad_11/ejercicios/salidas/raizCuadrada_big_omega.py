def raizCuadrada(n):  # funcion raizCuadrada: Ω(log n)
    if n < 0:  # Ω(1)
        return None  # Ω(1)  (rama no ejecutada en el mejor caso)
    x = n  # Ω(1)
    y = (x + 1) // 2  # Ω(1)
    while y < x:  # Ω(log n)  (la variable de control se divide o multiplica en cada vuelta)
        x = y  # Ω(1) x Ω(log n) = Ω(log n)
        y = (x + n // x) // 2  # Ω(1) x Ω(log n) = Ω(log n)
    return x  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion raizCuadrada
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(1) + Ω(log n) + Ω(log n) + Ω(log n) + Ω(1)
#     = 3 log n + 4
#   Complejidad de mayor grado: Ω(log n)
# ==========================================================================
