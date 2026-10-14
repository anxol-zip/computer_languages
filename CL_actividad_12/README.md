# Actividad 12 — Búsqueda informada en grafos: Greedy y A*

**Materia:** Lenguajes de Computación · Otoño 2026

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

---

## Descripción

Backend en **FastAPI** que busca una ruta entre dos nodos de un grafo **dirigido y ponderado** con
dos algoritmos de búsqueda informada, implementados a mano (sin librerías de grafos):

- **Greedy Best-First Search** ([`greedy_search.py`](./src/busqueda/greedy_search.py)): expande
  siempre el nodo que *parece* más cercano al destino (menor $h(n)$).
- **A\*** ([`star_search.py`](./src/busqueda/star_search.py)): expande el nodo con menor
  $f(n) = g(n) + h(n)$, es decir, el costo ya recorrido más la estimación de lo que falta.

El servicio sigue creciendo sobre las actividades anteriores: los endpoints de la Actividad 6 y de la
Actividad 11 siguen disponibles sin cambios.

| Endpoint | Método | Actividad | Qué hace |
|---|---|---|---|
| `/afd/evaluar` | POST | 6 | Evalúa cadenas sobre un AFD |
| `/afn/evaluar` | POST | 6 | Evalúa cadenas sobre un AFN (con o sin transiciones ε) |
| `/complejidad/peor-caso` | POST | 11 | Anota un programa `.py` con su complejidad Big-O |
| `/complejidad/mejor-caso` | POST | 11 | Anota un programa `.py` con su complejidad Big-Omega |
| `/search/greedy` | POST | **12** | Búsqueda voraz |
| `/search/star` | POST | **12** | Búsqueda A\* |

## Estructura del proyecto

```
CL_actividad_12/
├── main.py                  # crea la app y conecta los endpoints de los 3 módulos
├── src/
│   ├── automatas/           # Actividad 6 (sin cambios)
│   ├── complejidad/         # Actividad 11 (sin cambios)
│   └── busqueda/            # Actividad 12
│       ├── esquemas.py      #   Pydantic: entrada y salida
│       ├── heuristica.py    #   h(n): por saltos o euclidiana
│       ├── greedy_search.py #   Greedy Best-First Search
│       ├── star_search.py   #   A*
│       ├── utilidades.py    #   reconstruir la ruta y sumar su costo
│       ├── ejemplos.py      #   las 9 pruebas como ejemplos de /docs
│       └── rutas.py         #   POST /search/greedy, POST /search/star
├── grafos/
│   ├── grafo_N.json         # los grafos del archivo del profesor (N = 10, 25, 50)
│   └── coordenadas_N.json   # posición (x, y) de cada nodo, medida en las imágenes
├── medir_coordenadas.py     # genera coordenadas_N.json a partir de material/*.png
├── material/                # archivos del profesor (.txt e imágenes de los grafos)
├── pyproject.toml, uv.lock  # dependencias (uv)
└── .python-version          # Python 3.14
```

Los grafos de `grafos/` son los del `.txt` del profesor, sin cambiar ninguna arista. El `.txt` no es
JSON válido tal cual (al grafo de 10 le sobra una coma y al de 50 le falta la llave de cierre), por
eso se guardaron aparte, ya corregidos.

| Grafo | Nodos $V$ | Aristas $E$ | Peso mínimo |
|---|---|---|---|
| `grafo_10` | 10 | 17 | 8 |
| `grafo_25` | 25 | 45 | 5 |
| `grafo_50` | 50 | 56 | 12 |

## Cómo correr y probar

```bash
uv sync                  # instala las dependencias
uv run fastapi dev       # servidor en http://127.0.0.1:8000  (o bien: uv run main.py)
```

Para probar, entra a `http://127.0.0.1:8000/docs`, abre `/search/greedy` o `/search/star`, da clic en
**Try it out**, elige una prueba del menú **Examples** (por ejemplo `grafo_25 A-Y saltos`) y da clic
en **Execute**. Las 9 pruebas de la actividad están precargadas, cada una con las 3 heurísticas.

# Entrada y salida (Pydantic)

**Entrada** — `SolicitudBusqueda`:

| Campo | Obligatorio | Descripción |
|---|---|---|
| `grafo` | Sí | Lista de adyacencia con pesos: `{"A": [["B", 15], ["C", 22]], ...}` (el formato del `.txt`) |
| `origen`, `destino` | Sí | Nodos del grafo |
| `limite_nodos` | No | Máximo de nodos a visitar. **Por defecto, el 80 % de los nodos**: 8, 20 y 40 |
| `coordenadas` | No | `{"A": [x, y], ...}`. Si se manda, $h$ es euclidiana; si no, por saltos |
| `escalar_heuristica` | No | Solo con coordenadas. `true` (por defecto): distancia × $k$. `false`: distancia cruda |

Si algo no es válido (un vecino o un origen/destino que no está en el grafo, pesos negativos, un
límite mayor que el número de nodos, coordenadas incompletas), la API responde **422** con el motivo.

**Salida** — `ResultadoBusqueda` (respuesta de `/search/star`, grafo de 10, A → J, saltos; `tiempo_ms` cambia en cada ejecución):

```json
{
  "algoritmo": "A*", "origen": "A", "destino": "J",
  "heuristica": "saltos al destino x peso minimo", "factor_escala": null,
  "limite_nodos": 8,
  "nodos_visitados": 8,
  "solucion": true,
  "ruta": ["A", "B", "F", "I", "J"],
  "costo": 56.0,
  "orden_visita": ["A", "D", "C", "B", "G", "F", "I", "J"],
  "T(n)": {"cota": "O((V + E) log V)", "V": 10, "E": 17, "operaciones": 23, "tiempo_ms": 0.03},
  "S(n)": {"cota": "O(V + E)", "max_nodos_en_memoria": 12}
}
```

Los cinco campos que pide la actividad son `nodos_visitados`, `solucion`, `ruta`, `T(n)` y `S(n)`.
`nodos_visitados` cuenta los nodos **expandidos** (los que salen de la lista abierta), y es lo que se
compara contra el límite. El resto (`costo`, `orden_visita`, …) sirve para comparar los algoritmos.

# Heurísticas h(n)

La instrucción pide una heurística "como la distancia euclidiana", pero el `.txt` solo trae aristas y
pesos: las posiciones de los nodos solo aparecen en las imágenes. Por eso hay dos heurísticas
([`heuristica.py`](./src/busqueda/heuristica.py)), y **las dos son consistentes** (nunca
sobreestiman el costo real), así que A\* siempre regresa la ruta de menor costo.

### 1. Por saltos (por defecto)

$$h(n) = \text{saltos}(n, d) \cdot w_{\min}$$

$\text{saltos}(n, d)$ es el menor número de aristas de $n$ al destino $d$, calculado con una **BFS**
(la de clase) sobre las aristas invertidas, empezando en el destino. $w_{\min}$ es el peso más chico
del grafo. Un camino de $k$ aristas cuesta al menos $k \cdot w_{\min}$, así que $h$ nunca
sobreestima. Un nodo sin camino al destino tiene $h = \infty$ y se explora al final.

### 2. Euclidiana, con coordenadas medidas en las imágenes

[`medir_coordenadas.py`](./medir_coordenadas.py) mide la posición de cada nodo en los PNG, para que
cualquiera pueda obtener exactamente los mismos números:

1. Marca los pixeles del azul de relleno de los nodos, `(42, 142, 230)`.
2. Agrupa los pixeles azules que se tocan con una **BFS sobre la rejilla de pixeles**: cada grupo es
   un círculo, y el centro de su caja envolvente es la coordenada del nodo.
3. Le pone a cada círculo la letra más cercana de una tabla aproximada, leída una sola vez de las
   imágenes.
4. Se detiene sin escribir nada si no encuentra exactamente N círculos o si una letra se repite.

> **El script no forma parte de la API.** Se corre una sola vez, aparte del servidor
> (`uv run python medir_coordenadas.py`), y su resultado son los archivos `grafos/coordenadas_N.json`.
> Los endpoints no aceptan imágenes: solo reciben JSON con la lista de adyacencia y, si se quiere la
> heurística euclidiana, el campo `coordenadas` con los pares $(x, y)$ de cada nodo. Para usar un grafo
> nuevo con la euclidiana, primero hay que obtener sus coordenadas (con este script, si la imagen tiene
> el mismo estilo, o de cualquier otra forma) y mandarlas en la solicitud.

Las distancias quedan en pixeles (de ~190 a ~2000 entre vecinos), mientras que los pesos van de 5 a
85. Usada tal cual, la distancia sobreestimaría por mucho, así que se **escala**:

$$k = \min_{(u,v) \in E} \frac{c(u, v)}{\text{dist}(u, v)}, \qquad h(n) = k \cdot \text{dist}(n, d)$$

Con ese $k$, ninguna arista es más barata que su distancia escalada y, por la desigualdad del
triángulo, $h(u) \le c(u, v) + h(v)$: la heurística es consistente. Es la misma idea del ejemplo de
clase CDMX → SLP, donde los km por carretera nunca son menos que los km en línea recta.

| Grafo | $k$ | Arista que lo fija |
|---|---|---|
| `grafo_10` | 0.0164 | A → C: peso 22, 1339 px |
| `grafo_25` | 0.0117 | J → M: peso 10, 853 px |
| `grafo_50` | 0.0336 | AR → AX: peso 25, 744 px |

Para comparar, la API también acepta la distancia **cruda** (sin escalar):

| | Euclidiana (escalada) | Euclidiana cruda |
|---|---|---|
| Fórmula | $h(n) = k \cdot \text{dist}(n, d)$ | $h(n) = \text{dist}(n, d)$, en pixeles |
| ¿Admisible? | Sí: nunca sobreestima | No: cientos de pixeles contra pesos de 5 a 85 |
| Efecto en A\* | Siempre óptimo (452 de 452 pares) | $h$ aplasta a $g$, se comporta como greedy y no es óptimo en 71 de 452 pares |
| Cómo se pide | `"escalar_heuristica": true` (por defecto) | `"escalar_heuristica": false` |

> De las imágenes solo se toman **posiciones**; las aristas salen del `.txt`. Las imágenes no
> coinciden del todo con el `.txt`: la de 50 nodos, por ejemplo, no dibuja `A → C` y dibuja muchas
> más flechas que sus 56 aristas.

# Algoritmos

| | Greedy Best-First Search | A\* |
|---|---|---|
| Criterio | Menor $h(n)$; empates por menor peso de la arista y luego por orden alfabético | Menor $f(n) = g(n) + h(n)$; empates por menor $h$ y luego por orden alfabético |
| ¿Corrige decisiones? | No: un nodo se queda con el primer padre que lo descubre | Sí: si encuentra un camino más barato a un nodo, actualiza su $g$ y su padre |
| ¿Ruta óptima? | No garantizada | Sí, con $h$ consistente |

**Ejemplo — grafo de 10 nodos, A → J, heurística por saltos** ($h$: A = B = 24, C = D = E = F = 16,
G = H = I = 8, J = 0):

- **Greedy:** de A pasa a D ($h = 16$; empata con C, pero gana por peso 10 < 22), luego a G
  ($h = 8$) y luego a J ($h = 0$). Ruta **A → D → G → J, costo 90**, con 4 visitas. Eligió
  G → J (50) porque J tiene $h = 0$, sin ver que G → I → J cuesta 18.
- **A\*:** también llega a generar J por G con $f = 90$, pero no lo acepta mientras haya nodos con
  $f$ menor. Al expandir B descubre que F sale más barato por B ($g = 33$) que por D ($g = 38$), y por
  ahí llega a J con $f = 56$. Ruta **A → B → F → I → J, costo 56**, con 8 visitas.

# Complejidad: T(n) y S(n)

La lista abierta es un montículo binario (`heapq`, de la biblioteca estándar: solo la estructura de
datos, no un algoritmo de búsqueda).

| | Greedy | A\* |
|---|---|---|
| $T(n)$ | $O((V + E) \log V)$ | $O((V + E) \log V)$ |
| $S(n)$ | $O(V)$ | $O(V + E)$ |

Cada arista se revisa a lo más una vez y cada operación del heap cuesta $O(\log V)$. En A\* un nodo
puede volver a entrar al heap cada vez que mejora su $g$; de ahí el $O(V + E)$ en espacio. La
heurística por saltos agrega una BFS previa de $O(V + E)$, que no cambia el orden.

En la respuesta, `T(n).operaciones` cuenta las extracciones del heap más las aristas revisadas (es la
medida que se usa para comparar), `T(n).tiempo_ms` es tiempo de reloj (varía entre ejecuciones) y
`S(n).max_nodos_en_memoria` es el máximo de entradas en las listas abierta y cerrada al mismo tiempo.

# Pruebas y resultados

Tres pruebas por grafo, con distintos orígenes y destinos y con el límite por defecto (80 %).

### Con la heurística por saltos

| Grafo | Prueba | Algoritmo | Visitados | Solución | Ruta | Costo | T(n) ops | S(n) |
|---|---|---|---|---|---|---|---|---|
| 10 | A → J | Greedy | 4 / 8 | True | A → D → G → J | 90 | 11 | 8 |
| 10 | A → J | A\* | 8 / 8 | True | A → B → F → I → J | **56** | 23 | 12 |
| 10 | B → H | Greedy | 3 / 8 | True | B → F → H | 58 | 7 | 5 |
| 10 | B → H | A\* | 4 / 8 | True | B → E → H | **47** | 10 | 6 |
| 10 | D → I | Greedy | 3 / 8 | True | D → F → I | 43 | 7 | 5 |
| 10 | D → I | A\* | 4 / 8 | True | D → G → I | **40** | 10 | 7 |
| 25 | A → Y | Greedy | 7 / 20 | True | A → D → I → M → R → U → Y | 142 | 20 | 14 |
| 25 | A → Y | A\* | 18 / 20 | True | A → D → F → K → R → U → Y | **115** | 56 | 23 |
| 25 | D → W | Greedy | 6 / 20 | True | D → I → M → R → T → W | 207 | 17 | 12 |
| 25 | D → W | A\* | 16 / 20 | True | D → F → K → R → T → W | **180** | 50 | 21 |
| 25 | B → V | Greedy | 5 / 20 | True | B → G → K → R → V | **82** | 16 | 12 |
| 25 | B → V | A\* | 13 / 20 | True | B → G → K → R → V | **82** | 43 | 19 |
| 50 | A → AA | Greedy | 5 / 40 | True | A → B → I → S → AA | 156 | 12 | 8 |
| 50 | A → AA | A\* | 8 / 40 | True | A → F → G → N → W → AA | **117** | 19 | 12 |
| 50 | E → AX | Greedy | 7 / 40 | True | E → O → P → AC → AN → AU → AX | **187** | 14 | 8 |
| 50 | E → AX | A\* | 9 / 40 | True | E → O → P → AC → AN → AU → AX | **187** | 18 | 10 |
| 50 | D → AM | Greedy | 9 / 40 | False | — | — | 18 | 9 |
| 50 | D → AM | A\* | 9 / 40 | False | — | — | 18 | 9 |

En **negritas**, el costo óptimo. D → AM no tiene camino: los dos algoritmos recorren los 9 nodos
alcanzables desde D y responden `false`.

### Comparación de heurísticas

Cada celda es **costo (nodos visitados)**. Greedy da exactamente lo mismo con la euclidiana escalada
que con la cruda (multiplicar todas las $h$ por $k$ no cambia su orden), así que aparece una sola vez.

| Grafo | Prueba | Greedy: saltos | Greedy: euclidiana | A\*: saltos | A\*: euclidiana | A\*: euclidiana cruda |
|---|---|---|---|---|---|---|
| 10 | A → J | 90 (4) | 75 (5) | **56** (8) | **56** (8) | 75 (5) |
| 10 | B → H | 58 (3) | **47** (3) | **47** (4) | **47** (3) | **47** (3) |
| 10 | D → I | 43 (3) | **40** (3) | **40** (4) | **40** (3) | **40** (3) |
| 25 | A → Y | 142 (7) | 160 (7) | **115** (18) | **115** (18) | 160 (7) |
| 25 | D → W | 207 (6) | **180** (9) | **180** (16) | sin solución (20) | **180** (8) |
| 25 | B → V | **82** (5) | 164 (5) | **82** (13) | **82** (15) | **82** (5) |
| 50 | A → AA | 156 (5) | 173 (5) | **117** (8) | **117** (11) | 173 (5) |
| 50 | E → AX | **187** (7) | **187** (7) | **187** (9) | **187** (9) | **187** (7) |

### Análisis

- **Greedy explora menos, A\* garantiza el óptimo.** Con saltos, greedy visitó 40 nodos en total
  contra 80 de A\*, e hizo de 1.3 a 2.9 veces menos operaciones. Pero solo encontró la ruta óptima en
  2 de 8 pruebas, y en las demás pagó entre 7.5 % y 61 % más. A\* fue óptimo en todas: su trabajo extra
  es el precio de **garantizar** la ruta más barata, no solo de encontrar una.
- **El límite de nodos también es un compromiso.** En A → J, A\* llega justo en la visita 8, que es el
  límite. Con `"limite_nodos": 7`, A\* responde `false` y greedy sigue dando su ruta de costo 90.
- **La euclidiana escalada es correcta, pero informa poco.** Un solo $k$ para todo el grafo, fijado
  por la arista más "comprimida" del dibujo, deja $h$ muy por debajo del costo real. En D → W eso hizo
  que A\* agotara las 20 visitas permitidas sin llegar (con límite 25 llega en 22). Las imágenes son
  un dibujo del grafo, no un mapa a escala.
- **Con pixeles crudos, A\* se vuelve greedy.** Las distancias crudas (cientos de pixeles) aplastan a
  $g$ (decenas), así que $f \approx h$, que es exactamente greedy, como se vio en clase. Por eso en 3
  pruebas regresa rutas que no son las óptimas (A → J, A → Y y A → AA).
- **La forma del grafo importa.** El grafo de 50 es casi un árbol (56 aristas para 50 nodos), así que
  hay pocas alternativas y greedy casi no se equivoca. En el de 25, con muchas rutas que se cruzan,
  falla más.

**Verificación.** Durante el desarrollo se comparó A\* contra Dijkstra en **todos** los pares
(origen, destino) con camino de los tres grafos (452 pares) con un script que ya no forma parte del
repositorio. Con saltos y con la euclidiana escalada, A\* fue óptimo en los 452. Con la euclidiana
cruda falló en 71, lo que confirma que sin escalar la heurística deja de ser admisible.

# Limitaciones

- La heurística por saltos recorre todo el grafo desde el destino antes de buscar: es como un GPS que
  ya tiene el mapa completo.
- La euclidiana depende de la calidad del dibujo. Con `escalar_heuristica: false` deja de ser
  admisible y A\* puede no regresar el óptimo.
- `medir_coordenadas.py` depende del estilo de las imágenes (el color azul de los nodos); si cambian,
  hay que ajustar `COLOR_NODO` y `TOLERANCIA`.
- Los grafos son dirigidos: `["B", 15]` en la lista de `A` va solo de A a B.
