# Actividad 12 - Lenguajes de Computacion
# Angel Rugerio Jimenez  #201720
#
# Corre las 9 pruebas de la actividad (3 por grafo) contra los dos endpoints, guarda
# cada respuesta en resultados/ y escribe la tabla comparativa en resultados/resumen.md.
# Usa el TestClient de FastAPI, asi que no hace falta levantar el servidor:
#
#     uv run python generar_resultados.py

import json
from pathlib import Path

from fastapi.testclient import TestClient

from main import app

RAIZ = Path(__file__).parent
GRAFOS = RAIZ / "grafos"
RESULTADOS = RAIZ / "resultados"

# (grafo, origen, destino) -- distintos origenes y destinos en cada grafo.
# El limite de nodos no se manda: se usa el de por defecto (80% de los nodos).
CASOS = [
    ("grafo_10", "A", "J"),
    ("grafo_10", "B", "H"),
    ("grafo_10", "D", "I"),
    ("grafo_25", "A", "Y"),
    ("grafo_25", "D", "W"),
    ("grafo_25", "B", "V"),
    ("grafo_50", "A", "AA"),
    ("grafo_50", "E", "AX"),
    ("grafo_50", "D", "AM"),
]
ENDPOINTS = {"greedy": "/search/greedy", "star": "/search/star"}

cliente = TestClient(app)
RESULTADOS.mkdir(exist_ok=True)

filas = [
    "| Grafo | Origen → Destino | Algoritmo | Visitados / límite | Solución | Ruta | Costo "
    "| T(n): operaciones | T(n): ms | S(n): máx. en memoria |",
    "|---|---|---|---|---|---|---|---|---|---|",
]

for nombre_grafo, origen, destino in CASOS:
    grafo = json.loads((GRAFOS / f"{nombre_grafo}.json").read_text(encoding="utf-8"))
    solicitud = {"grafo": grafo, "origen": origen, "destino": destino}

    for algoritmo, endpoint in ENDPOINTS.items():
        respuesta = cliente.post(endpoint, json=solicitud)
        respuesta.raise_for_status()
        datos = respuesta.json()

        archivo = RESULTADOS / f"{nombre_grafo}_{origen}-{destino}_{algoritmo}.json"
        archivo.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        ruta = " → ".join(datos["ruta"]) if datos["ruta"] else "—"
        costo = f"{datos['costo']:g}" if datos["costo"] is not None else "—"
        filas.append(
            f"| {nombre_grafo} | {origen} → {destino} | {datos['algoritmo']} "
            f"| {datos['nodos_visitados']} / {datos['limite_nodos']} | {datos['solucion']} "
            f"| {ruta} | {costo} | {datos['T(n)']['operaciones']} | {datos['T(n)']['tiempo_ms']} "
            f"| {datos['S(n)']['max_nodos_en_memoria']} |"
        )
        print(f"{endpoint:<15} {nombre_grafo} {origen:>2} -> {destino:<2}  -> resultados/{archivo.name}")

(RESULTADOS / "resumen.md").write_text("\n".join(filas) + "\n", encoding="utf-8")
print("tabla comparativa -> resultados/resumen.md")
