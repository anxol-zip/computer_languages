# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Muestra la traza de Karatsuba en un ejemplo pequeno y luego mide T(N) y S(N) de los
# cuatro metodos de multiplicacion con numeros de N digitos.
#
#   uv run main.py                traza de 1234 x 5678 y mediciones con 20, 50 y 100 digitos
#   uv run main.py 200 500 1000   solo las mediciones, con otros tamanos

import math
import random
import sys

from dyv import (medir, multiplicar_clasico, multiplicar_escolar, multiplicar_karatsuba,
                 multiplicar_python, numero_aleatorio)

SEMILLA = 14          # la misma semilla da siempre los mismos numeros
TAMANOS = [20, 50, 100]

METODOS = [
    ("Python  *", multiplicar_python),
    ("Escolar", multiplicar_escolar),
    ("DyV 4 llamadas", multiplicar_clasico),
    ("Karatsuba", multiplicar_karatsuba),
]


def mostrar_traza(x, y):
    print(f"=== Traza de Karatsuba: {x} x {y} ===\n")
    producto, contador = multiplicar_karatsuba(x, y, traza=True)
    print(f"\nResultado: {producto}   Python: {x * y}   "
          f"multiplicaciones de un digito: {contador.multiplicaciones}\n")


def comparar(n, rng):
    x = numero_aleatorio(n, rng)
    y = numero_aleatorio(n, rng)
    esperado = x * y

    print(f"=== N = {n} digitos ===")
    print(f"x = {x}\ny = {y}\nx * y = {esperado}")
    print(f"Referencia: N^2 = {n * n},  N^log2(3) = {n ** math.log2(3):.0f}\n")

    print(f"{'Metodo':<15}{'Correcto':>9}{'Mult. 1 dig':>13}{'Llamadas':>10}"
          f"{'Profundidad':>13}{'Tiempo (us)':>13}{'Memoria (KB)':>14}")
    for nombre, multiplicar in METODOS:
        producto, contador, tiempo_us, memoria_kb = medir(multiplicar, x, y)
        correcto = "si" if producto == esperado else "NO"
        if contador is None:                # Python * no expone sus conteos
            conteos = f"{'-':>13}{'-':>10}{'-':>13}"
        else:
            conteos = (f"{contador.multiplicaciones:>13}{contador.llamadas:>10}"
                       f"{contador.profundidad:>13}")
        print(f"{nombre:<15}{correcto:>9}{conteos}{tiempo_us:>13.2f}{memoria_kb:>14.2f}")
    print()


if __name__ == "__main__":
    # Python 3.14 limita int <-> str a 4300 digitos; el producto de dos numeros de
    # mas de 2150 digitos ya lo rebasa. Se quita el limite para poder probar tamanos grandes.
    sys.set_int_max_str_digits(0)

    tamanos = [int(n) for n in sys.argv[1:]]
    if not tamanos:
        mostrar_traza(1234, 5678)
        tamanos = TAMANOS

    rng = random.Random(SEMILLA)
    for n in tamanos:
        comparar(n, rng)
