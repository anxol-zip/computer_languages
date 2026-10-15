# Actividad 13 — Algoritmos P, NP y con heurística

**Materia:** Lenguajes de Computación · Otoño 2026

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

---

## Descripción

Backend en **FastAPI** que continúa el de las actividades anteriores y agrega tres algoritmos sobre
grafos ponderados, más un generador de grafos de prueba:

- **Dijkstra**: camino más corto entre dos nodos (clase **P**).
- **Agente viajero exacto**: recorrido más barato que visita todos los nodos (**NP-difícil**).
- **Agente viajero voraz**: heurística del vecino más cercano.

Cada algoritmo regresa el **tiempo de ejecución (ms)**, la **memoria consumida (KB)**, los **nodos
recorridos** y el **costo** del camino encontrado.

📄 **La documentación de cada algoritmo y las pruebas con 5, 10 y 15 nodos están en
[`ALGORITMOS.md`](./ALGORITMOS.md).**

| Endpoint | Método | Actividad | Qué hace |
|---|---|---|---|
| `/afd/evaluar`, `/afn/evaluar` | POST | 6 | Evalúan cadenas sobre un AFD / AFN |
| `/complejidad/peor-caso`, `/complejidad/mejor-caso` | POST | 11 | Anotan un `.py` con Big-O / Big-Omega |
| `/search/greedy`, `/search/star` | POST | 12 | Búsqueda informada Greedy y A\* |
| `/grafos/sintetico` | POST | **13** | Genera un grafo ponderado aleatorio |
| `/grafos/dijkstra` | POST | **13** | Dijkstra |
| `/grafos/tsp` | POST | **13** | Agente viajero exacto (hasta 15 nodos) |
| `/grafos/tsp-voraz` | POST | **13** | Agente viajero con heurística voraz |

## Cómo correr y probar

```bash
uv sync                  # instala las dependencias
uv run fastapi dev       # servidor en http://127.0.0.1:8000  (o bien: uv run main.py)
```

Entra a `http://127.0.0.1:8000/docs`, abre un endpoint de `/grafos`, da clic en **Try it out**, elige
una prueba del menú **Examples** (`grafo de 5 nodos`, `grafo de 10 nodos` o `grafo de 15 nodos`) y da
clic en **Execute**.

Para probar con otro grafo: genera uno en `/grafos/sintetico` y copia el campo `grafo` de la respuesta
a la solicitud de `/grafos/dijkstra`, `/grafos/tsp` o `/grafos/tsp-voraz`.

## Estructura del proyecto

```
CL_actividad_13/
├── main.py                 # crea la app y conecta los endpoints de los 4 módulos
├── ALGORITMOS.md           # documentación de los algoritmos y pruebas
├── src/
│   ├── automatas/          # Actividad 6
│   ├── complejidad/        # Actividad 11
│   ├── busqueda/           # Actividad 12
│   └── pnp/                # Actividad 13
│       ├── esquemas.py     #   Pydantic: entrada y salida
│       ├── sintetico.py    #   generador de grafos
│       ├── dijkstra.py     #   Dijkstra
│       ├── tsp_exacto.py   #   agente viajero exacto
│       ├── tsp_voraz.py    #   agente viajero voraz
│       ├── medicion.py     #   tiempo y memoria
│       ├── ejemplos.py     #   las 3 pruebas como ejemplos de /docs
│       └── rutas.py        #   endpoints /grafos/...
├── pyproject.toml, uv.lock # dependencias (uv)
└── .python-version         # Python 3.14
```

> Los endpoints de la Actividad 12 siguen funcionando, pero sin los archivos de grafos y coordenadas
> de esa actividad: sus ejemplos en `/docs` usan ahora el grafo de 10 nodos del profesor con la
> heurística por saltos. La heurística euclidiana sigue disponible si se mandan `coordenadas`.
