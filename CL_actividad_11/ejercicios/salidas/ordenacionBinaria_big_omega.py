def ordenacionBinaria(lista, objetivo):  # funcion ordenacionBinaria: Ω(1)
    izquierda, derecha = 0, len(lista) - 1  # Ω(1)
    while izquierda <= derecha:  # Ω(1)  (salida temprana: en el mejor caso termina en la 1a iteracion)
        medio = (izquierda + derecha) // 2  # Ω(1)
        if lista[medio] == objetivo:  # Ω(1)
            return medio  # Ω(1)
        elif lista[medio] < objetivo:  # Ω(1)
            izquierda = medio + 1  # Ω(1)  (rama no ejecutada en el mejor caso)
        else:
            derecha = medio - 1  # Ω(1)  (rama no ejecutada en el mejor caso)
    return -1  # Ω(1)


# ==========================================================================
# RESUMEN DE COMPLEJIDAD -- MEJOR CASO (Big-Omega)
# ==========================================================================
# Funcion ordenacionBinaria
#   Suma de complejidades individuales:
#     Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1) + Ω(1)
#     = 7
#   Complejidad de mayor grado: Ω(1)
# ==========================================================================
