# Actividad 12 - Lenguajes de Computacion (reutilizada en la Actividad 13)
# Angel Rugerio Jimenez  #201720
#
# Ejemplos precargados para la documentacion interactiva (/docs). En la Actividad 13
# ya no se incluyen los archivos de grafos ni las coordenadas de la Actividad 12, asi
# que los ejemplos usan el grafo de 10 nodos del profesor (GRAFO_EJEMPLO) con la
# heuristica por saltos. Cualquier grafo de /grafos/sintetico tambien sirve aqui.

from busqueda.esquemas import GRAFO_EJEMPLO

CASOS = [("A", "J"), ("B", "H"), ("D", "I")]

EJEMPLOS = {
    f"grafo_10 {origen}-{destino}": {
        "summary": f"Grafo de 10 nodos: {origen} -> {destino} (heuristica: saltos)",
        "value": {"grafo": GRAFO_EJEMPLO, "origen": origen, "destino": destino},
    }
    for origen, destino in CASOS
}
