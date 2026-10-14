# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Obtiene la posicion (x, y) de cada nodo a partir de las imagenes del profesor
# (material/grafo-N-nodos.png) y la guarda en grafos/coordenadas_N.json, para usarla
# en la heuristica euclidiana. Solo se toman POSICIONES de las imagenes: las aristas y
# los pesos siguen saliendo de grafos/grafo_N.json.
#
# Pasos por imagen:
#   1. Mascara: pixeles cuyo color esta cerca del relleno azul de los nodos.
#   2. Componentes conexas de la mascara con una BFS -> un circulo por componente.
#   3. Centro de cada circulo = centro de su caja envolvente (la letra blanca del
#      centro hace un hueco en la mascara, pero no cambia la caja).
#   4. Etiqueta: cada centro se asigna al nodo de APROXIMADAS mas cercano. Esa tabla
#      se escribio una sola vez leyendo las imagenes; el script solo la usa para poner
#      nombre, la posicion exacta sale de los pixeles.
#   5. Si algo no cuadra (numero de circulos, asignacion que no es 1 a 1, centro lejos
#      de su aproximado) el script se detiene en vez de escribir coordenadas malas.
#
# Coordenadas en pixeles de la imagen original (2779 x 1981): origen arriba a la
# izquierda, y crece hacia abajo. El sentido de y no cambia ninguna distancia.
#
#     uv run python medir_coordenadas.py

import json
import math
from collections import deque
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).parent
MATERIAL = RAIZ / "material"
GRAFOS = RAIZ / "grafos"

COLOR_NODO = (42, 142, 230)     # relleno azul de los circulos (muestreado de los PNG)
TOLERANCIA = 40                 # distancia RGB maxima para contar como relleno
AREA_MINIMA = 500               # componentes mas chicas son ruido (bordes de flechas, etc.)

# Posicion aproximada de cada nodo, leida a ojo de las imagenes (pixeles originales,
# redondeados a decenas). Solo sirve para saber que letra es cada circulo detectado.
APROXIMADAS = {
    10: {
        "A": (2120, 270), "B": (2320, 760), "C": (790, 430), "D": (2520, 500),
        "E": (390, 1110), "F": (2120, 1370), "G": (1940, 1550), "H": (260, 1530),
        "I": (1430, 1700), "J": (1000, 1800),
    },
    25: {
        "A": (260, 1040),
        "B": (640, 460), "D": (640, 840), "E": (640, 1230), "C": (640, 1610),
        "H": (1010, 270), "G": (1010, 650), "F": (1010, 1040), "I": (1010, 1420), "J": (1010, 1800),
        "N": (1390, 270), "K": (1390, 650), "M": (1390, 1040), "O": (1390, 1420), "L": (1390, 1800),
        "T": (1770, 270), "S": (1770, 650), "R": (1770, 1040), "P": (1770, 1420), "Q": (1770, 1800),
        "W": (2150, 460), "V": (2150, 840), "U": (2150, 1230), "X": (2150, 1610),
        "Y": (2520, 1040),
    },
    50: {
        "A": (260, 1040),
        "B": (580, 560), "G": (580, 750), "F": (580, 940), "C": (580, 1130), "E": (580, 1320),
        "D": (580, 1510),
        "H": (900, 370), "N": (900, 560), "I": (900, 750), "K": (900, 940), "M": (900, 1130),
        "O": (900, 1320), "L": (900, 1510), "J": (900, 1700),
        "T": (1230, 270), "W": (1230, 460), "S": (1230, 650), "R": (1230, 840), "V": (1230, 1040),
        "P": (1230, 1230), "Q": (1230, 1420), "U": (1230, 1610), "X": (1230, 1800),
        "Y": (1550, 270), "AA": (1550, 460), "AD": (1550, 650), "AB": (1550, 840), "AC": (1550, 1040),
        "AF": (1550, 1230), "AE": (1550, 1420), "Z": (1550, 1610), "AG": (1550, 1800),
        "AJ": (1880, 370), "AM": (1880, 560), "AO": (1880, 750), "AN": (1880, 940),
        "AL": (1880, 1130), "AI": (1880, 1320), "AK": (1880, 1510), "AH": (1880, 1700),
        "AR": (2200, 370), "AV": (2200, 560), "AW": (2200, 750), "AU": (2200, 940),
        "AQ": (2200, 1130), "AT": (2200, 1320), "AP": (2200, 1510), "AS": (2200, 1700),
        "AX": (2520, 1040),
    },
}


def es_relleno(color):
    return sum((a - b) ** 2 for a, b in zip(color, COLOR_NODO)) <= TOLERANCIA ** 2


def detectar_circulos(imagen):
    """Regresa [(x_centro, y_centro, diametro)] de cada componente azul grande."""
    ancho, alto = imagen.size
    pixeles = imagen.load()
    mascara = [[es_relleno(pixeles[x, y]) for x in range(ancho)] for y in range(alto)]
    visto = [[False] * ancho for _ in range(alto)]
    circulos = []

    for y in range(alto):
        for x in range(ancho):
            if not mascara[y][x] or visto[y][x]:
                continue
            # BFS: todos los pixeles de relleno conectados a (x, y)
            visto[y][x] = True
            cola = deque([(x, y)])
            area = 0
            x_min = x_max = x
            y_min = y_max = y
            while cola:
                cx, cy = cola.popleft()
                area += 1
                x_min, x_max = min(x_min, cx), max(x_max, cx)
                y_min, y_max = min(y_min, cy), max(y_max, cy)
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < ancho and 0 <= ny < alto and mascara[ny][nx] and not visto[ny][nx]:
                        visto[ny][nx] = True
                        cola.append((nx, ny))
            if area >= AREA_MINIMA:
                circulos.append(((x_min + x_max) / 2, (y_min + y_max) / 2, x_max - x_min))
    return circulos


def etiquetar(circulos, aproximadas):
    """Asigna cada circulo al nodo aproximado mas cercano y valida la asignacion."""
    if len(circulos) != len(aproximadas):
        raise SystemExit(f"Se detectaron {len(circulos)} circulos, se esperaban {len(aproximadas)}.")

    coordenadas = {}
    for x, y, diametro in circulos:
        nodo = min(aproximadas, key=lambda n: math.dist((x, y), aproximadas[n]))
        error = math.dist((x, y), aproximadas[nodo])
        if error > diametro / 2:
            raise SystemExit(f"El circulo en ({x}, {y}) esta a {error:.0f} px de {nodo}: mas que un radio.")
        if nodo in coordenadas:
            raise SystemExit(f"Dos circulos se asignaron al nodo {nodo}.")
        coordenadas[nodo] = [x, y]
    return {nodo: coordenadas[nodo] for nodo in aproximadas}   # mismo orden que la tabla


for n, aproximadas in APROXIMADAS.items():
    imagen = Image.open(MATERIAL / f"grafo-{n}-nodos.png").convert("RGB")
    circulos = detectar_circulos(imagen)
    coordenadas = etiquetar(circulos, aproximadas)

    grafo = json.loads((GRAFOS / f"grafo_{n}.json").read_text(encoding="utf-8"))
    if set(coordenadas) != set(grafo):
        raise SystemExit(f"Los nodos de la imagen de {n} no son los mismos que los de grafo_{n}.json.")

    archivo = GRAFOS / f"coordenadas_{n}.json"
    archivo.write_text(
        "{\n" + ",\n".join(f"  {json.dumps(nodo)}: {json.dumps(xy)}" for nodo, xy in coordenadas.items()) + "\n}\n",
        encoding="utf-8",
    )
    diametro = circulos[0][2]
    print(f"grafo_{n}: {len(circulos)} circulos (diametro {diametro} px) -> {archivo.name}")
