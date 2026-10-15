# Actividad 13 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Ejemplos precargados para la documentacion interactiva (/docs): las pruebas de la
# actividad con grafos de 5, 10 y 15 nodos. Los grafos no se guardan en archivos: se
# generan con el mismo generador del endpoint /grafos/sintetico y una semilla fija,
# asi que son exactamente los que regresa ese endpoint con los mismos parametros.

from pnp.sintetico import generar_grafo

# (nodos, semilla, destino de Dijkstra) de cada prueba; grafo completo y pesos de 1 a 100
# (los valores por defecto). Los destinos se eligieron para que el camino mas corto
# no sea la arista directa desde A.
PRUEBAS = [(5, 5, "C"), (10, 10, "D"), (15, 15, "H")]

EJEMPLOS_SINTETICO = {}
EJEMPLOS_DIJKSTRA = {}
EJEMPLOS_TSP = {}

for n, semilla, destino in PRUEBAS:
    grafo, _ = generar_grafo(n, 1.0, 1, 100, semilla)
    nombre = f"grafo de {n} nodos"

    EJEMPLOS_SINTETICO[nombre] = {
        "summary": f"{n} nodos, semilla {semilla}",
        "value": {"nodos": n, "semilla": semilla},
    }
    EJEMPLOS_DIJKSTRA[nombre] = {
        "summary": f"{n} nodos: A -> {destino}",
        "value": {"grafo": grafo, "origen": "A", "destino": destino},
    }
    EJEMPLOS_TSP[nombre] = {
        "summary": f"{n} nodos: recorrido desde A",
        "value": {"grafo": grafo, "origen": "A"},
    }
