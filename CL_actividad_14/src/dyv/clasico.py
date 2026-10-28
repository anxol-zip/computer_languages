# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Divide y venceras "directo", con 4 multiplicaciones recursivas.
#
# Es el mismo esquema de Karatsuba pero sin su truco: con x = a*10^m + b y
# y = c*10^m + d, calcula los cuatro productos ac, ad, bc y bd. Dividir no ahorra
# nada: T(N) = 4 T(N/2) + O(N) = O(N^2), igual que la escolar. Sirve para ver que la
# mejora de Karatsuba viene de bajar de 4 a 3 subproblemas, no solo de dividir.

from dyv.digitos import aplicar_signo, desplazar, num_digitos, partir
from dyv.medicion import Contador


def clasico(x, y, contador, nivel=1):
    """x * y con x, y >= 0."""
    contador.entrar(nivel)

    if x == 0 or y == 0:                  # por cero no hace falta multiplicar
        return 0
    if x < 10 and y < 10:                 # caso base: un digito por un digito
        contador.multiplicaciones += 1
        return x * y

    # 1. Division
    m = max(num_digitos(x), num_digitos(y)) // 2
    a, b = partir(x, m)
    c, d = partir(y, m)

    # 2. Conquista: cuatro subproblemas
    ac = clasico(a, c, contador, nivel + 1)
    ad = clasico(a, d, contador, nivel + 1)
    bc = clasico(b, c, contador, nivel + 1)
    bd = clasico(b, d, contador, nivel + 1)

    # 3. Combinacion
    return desplazar(ac, 2 * m) + desplazar(ad + bc, m) + bd


def multiplicar_clasico(x, y):
    """Regresa (x * y, contador)."""
    contador = Contador()
    producto = clasico(abs(x), abs(y), contador)
    return aplicar_signo(x, y, producto), contador
