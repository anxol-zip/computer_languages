# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Tiempo de ejecucion y memoria consumida por un algoritmo.
#
# tracemalloc registra cada reserva de memoria de Python, lo que hace mas lento al
# algoritmo. Por eso se ejecuta dos veces: la primera solo se cronometra y la segunda
# solo mide el pico de memoria. Los algoritmos son deterministas: las dos ejecuciones
# hacen exactamente el mismo trabajo.

import time
import tracemalloc


def medir(algoritmo, *argumentos):
    """Regresa (resultado, tiempo en ms, pico de memoria en KB)."""
    inicio = time.perf_counter()
    resultado = algoritmo(*argumentos)
    tiempo_ms = (time.perf_counter() - inicio) * 1000

    tracemalloc.start()
    algoritmo(*argumentos)
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return resultado, tiempo_ms, pico / 1024
