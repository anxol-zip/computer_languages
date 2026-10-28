# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Algoritmo de Karatsuba (1960), en su forma recursiva.
#
# Se parte cada numero en mitad alta y mitad baja:
#     x = a * 10^m + b        y = c * 10^m + d
#     x * y = ac * 10^(2m) + (ad + bc) * 10^m + bd
#
# El truco: ad + bc no necesita dos multiplicaciones, sale de una sola,
#     (a + b)(c + d) = ac + ad + bc + bd   ->   ad + bc = (a + b)(c + d) - ac - bd
# y ac, bd ya estaban calculados. Son 3 subproblemas de la mitad de tamano en vez de 4:
#     T(N) = 3 T(N/2) + O(N) = O(N^log2(3)) ~ O(N^1.585)

from dyv.digitos import aplicar_signo, desplazar, num_digitos, partir
from dyv.medicion import Contador


def karatsuba(x, y, contador, nivel=1):
    """x * y con x, y >= 0."""
    contador.entrar(nivel)
    sangria = "    " * (nivel - 1)

    if x == 0 or y == 0:                  # por cero no hace falta multiplicar
        if contador.traza:
            print(f"{sangria}{x} x {y} = 0   (por cero, sin multiplicar)")
        return 0
    if x < 10 and y < 10:                 # caso base: un digito por un digito
        contador.multiplicaciones += 1
        producto = x * y
        if contador.traza:
            print(f"{sangria}{x} x {y} = {producto}   (caso base)")
        return producto

    # 1. Division: cada numero en mitad alta y mitad baja (m digitos en la baja)
    m = max(num_digitos(x), num_digitos(y)) // 2
    a, b = partir(x, m)
    c, d = partir(y, m)
    if contador.traza:
        print(f"{sangria}{x} x {y}  ->  a={a}, b={b}, c={c}, d={d}  (m={m})")

    # 2. Conquista: tres subproblemas mas pequenos, resueltos con la misma funcion
    ac = karatsuba(a, c, contador, nivel + 1)
    bd = karatsuba(b, d, contador, nivel + 1)
    suma = karatsuba(a + b, c + d, contador, nivel + 1)
    ad_mas_bc = suma - ac - bd

    # 3. Combinacion: x * y = ac * 10^(2m) + (ad + bc) * 10^m + bd
    resultado = desplazar(ac, 2 * m) + desplazar(ad_mas_bc, m) + bd
    if contador.traza:
        print(f"{sangria}= {ac}*10^{2 * m} + {ad_mas_bc}*10^{m} + {bd} = {resultado}")
    return resultado


def multiplicar_karatsuba(x, y, traza=False):
    """Regresa (x * y, contador)."""
    contador = Contador(traza)
    producto = karatsuba(abs(x), abs(y), contador)
    return aplicar_signo(x, y, producto), contador
