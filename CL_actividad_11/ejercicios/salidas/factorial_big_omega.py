def factorial(n):  # funcion factorial: Ω(n)
    if n < 0:  # Ω(1)
        return None  # Ω(1)  (rama no ejecutada en el mejor caso)
    resultado = 1  # Ω(1)
    for i in range(2, n + 1):  # Ω(n)
        resultado *= i  # Ω(1) x Ω(n) = Ω(n)
    return resultado  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion factorial
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(n) + Ω(n) + Ω(1)
#     = 2n + 3
#   Complejidad de mayor grado: Ω(n)
# ==========================================================================
