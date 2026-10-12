# Actividad 11 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Representacion de una complejidad y como escribirla (O(n^2), 2n + 4, ...).
# La usan las demas etapas: el analizador para calcular y el reporte para escribir.
#
# Cada complejidad se guarda como una tupla (e, k, j) que significa
#
#     (2^n)^e  *  n^k  *  (log n)^j
#
# Asi O(1) = (0, 0, 0), O(n) = (0, 1, 0), O(n log n) = (0, 1, 1), O(2^n) = (1, 0, 0).
# Multiplicar dos complejidades es sumar sus exponentes, y comparar tuplas en orden
# (e, k, j) es justo comparar tasas de crecimiento: cualquier exponencial le gana a
# cualquier polinomio, y cualquier n^k le gana a cualquier potencia de log n.

from collections import Counter

UNO = (0, 0, 0)
LOG_N = (0, 0, 1)
N = (0, 1, 0)
N_LOG_N = (0, 1, 1)
DOS_A_LA_N = (1, 0, 0)

# "peor" -> Big-O (cota superior), "mejor" -> Big-Omega (cota inferior)
SIMBOLOS = {"peor": "O", "mejor": "Ω"}


def multiplicar(a: tuple, b: tuple) -> tuple:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def termino(c: tuple) -> str:
    """Escribe la funcion de crecimiento sin la notacion: n^2, n log n, 2^n, 1."""
    partes = []
    if c[0] == 1:
        partes.append("2^n")
    elif c[0] > 1:
        partes.append(f"2^({c[0]}n)")
    if c[1] == 1:
        partes.append("n")
    elif c[1] > 1:
        partes.append(f"n^{c[1]}")
    if c[2] == 1:
        partes.append("log n")
    elif c[2] > 1:
        partes.append(f"log^{c[2]} n")
    return " ".join(partes) if partes else "1"


def notacion(c: tuple, modo: str) -> str:
    return f"{SIMBOLOS[modo]}({termino(c)})"


def polinomio(terminos: list) -> str:
    """Suma terminos iguales y los ordena de mayor a menor: [n, 1, n, 1] -> 2n + 2."""
    if not terminos:
        return "0"
    conteo = Counter(terminos)
    sumandos = []
    for c in sorted(conteo, reverse=True):
        veces = conteo[c]
        texto = termino(c)
        if texto == "1":
            sumandos.append(str(veces))
        elif veces == 1:
            sumandos.append(texto)
        elif texto.startswith("2^"):
            sumandos.append(f"{veces}({texto})")  # 2(2^n), no 22^n
        elif texto[0].isalpha():
            sumandos.append(f"{veces}{texto}" if texto[0] == "n" else f"{veces} {texto}")
        else:
            sumandos.append(f"{veces}{texto}")
    return " + ".join(sumandos)
