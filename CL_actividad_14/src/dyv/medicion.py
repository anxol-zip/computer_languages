# Actividad 14 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Medicion de T(N) y S(N) de cada algoritmo de multiplicacion.
#
# T(N) se mide de dos formas: contando las multiplicaciones de un digito que hace el
# algoritmo (no depende de la computadora) y cronometrando la ejecucion.
# S(N) tambien de dos formas: la profundidad maxima de la recursion (cuantas llamadas
# hay apiladas a la vez) y el pico de memoria reservada, medido con tracemalloc.
#
# tracemalloc hace mas lento al codigo que mide, asi que el tiempo y la memoria salen
# de ejecuciones distintas (igual que en la Actividad 13).

import time
import tracemalloc

REPETICIONES = 100    # el tiempo es el promedio de varias ejecuciones


class Contador:
    """Lo que hace un algoritmo mientras multiplica; se llena durante la ejecucion."""

    def __init__(self, traza=False):
        self.multiplicaciones = 0     # productos de un digito por un digito
        self.llamadas = 0             # veces que se llamo la funcion
        self.profundidad = 0          # maximo de llamadas apiladas a la vez
        self.traza = traza            # imprimir cada paso de la recursion

    def entrar(self, nivel):
        self.llamadas += 1
        self.profundidad = max(self.profundidad, nivel)


def multiplicar_python(x, y):
    """El operador * de Python, como referencia; no expone conteos."""
    return x * y, None


def medir(multiplicar, x, y, repeticiones=REPETICIONES):
    """Regresa (producto, contador, tiempo promedio en microsegundos, pico de memoria en KB)."""
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        multiplicar(x, y)
    tiempo_us = (time.perf_counter() - inicio) * 1_000_000 / repeticiones

    tracemalloc.start()
    producto, contador = multiplicar(x, y)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return producto, contador, tiempo_us, pico / 1024
