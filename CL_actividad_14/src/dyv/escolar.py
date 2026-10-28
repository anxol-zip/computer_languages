# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Multiplicacion escolar (la de primaria), sin divide y venceras.
#
# Cada digito de y se multiplica por cada digito de x y los productos parciales se
# suman con acarreo. Con dos numeros de N digitos son N * N multiplicaciones de un
# digito: T(N) = O(N^2). Es iterativa: no hay recursion.

from dyv.digitos import aplicar_signo
from dyv.medicion import Contador


def escolar(x, y, contador):
    """x * y con x, y >= 0."""
    contador.entrar(1)
    dx = [int(c) for c in reversed(str(x))]       # unidades primero
    dy = [int(c) for c in reversed(str(y))]
    resultado = [0] * (len(dx) + len(dy))

    for j, digito_y in enumerate(dy):
        acarreo = 0
        for i, digito_x in enumerate(dx):
            contador.multiplicaciones += 1
            total = resultado[i + j] + digito_x * digito_y + acarreo
            resultado[i + j] = total % 10
            acarreo = total // 10
        resultado[j + len(dx)] += acarreo

    return int("".join(str(d) for d in reversed(resultado)))


def multiplicar_escolar(x, y):
    """Regresa (x * y, contador)."""
    contador = Contador()
    producto = escolar(abs(x), abs(y), contador)
    return aplicar_signo(x, y, producto), contador
