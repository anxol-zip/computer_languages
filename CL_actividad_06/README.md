# Actividad 6 — Implementación de un evaluador de cadenas para un AFD y un AFN

**Materia:** Lenguajes de Computación · Otoño 2026

## Identificación del equipo

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |

**Nombre de la actividad:** Actividad 6 — Implementación de evaluador de cadenas para un AFD y un AFN.

---

## Descripción

Servicio web hecho con [FastAPI](https://fastapi.tiangolo.com/) ([`main.py`](./main.py)) que
expone **un endpoint por cada evaluador**: uno para autómatas finitos deterministas y otro para
autómatas finitos no deterministas (estos últimos con soporte de transiciones λ).

El desarrollo completo de los ejercicios, documentado paso a paso y con las llamadas reales a los
endpoints, está en [`Actividad_6.ipynb`](./Actividad_6.ipynb). Las definiciones de los autómatas
usados están en [`automatas.json`](./automatas.json).

## Endpoints

| Endpoint | Método | Autómata | δ |
|---|---|---|---|
| `/` | GET | — | Información del servicio |
| `/afd/evaluar` | POST | Determinista | $\delta: Q \times \Sigma \to Q$ |
| `/afn/evaluar` | POST | No determinista | $\delta: Q \times (\Sigma \cup \{\lambda\}) \to \mathcal{P}(Q)$ |

### Parámetros de entrada

Ambos endpoints reciben el mismo cuerpo JSON:

| Campo | Tipo | Descripción |
|---|---|---|
| `tabla_transicion` | objeto | `tabla[estado][símbolo] = destino` |
| `estado_inicial` | cadena | $q_0$ |
| `estados_finales` | lista | $F$ |
| `cadenas` | lista | Cadena(s) a evaluar (`""` es λ) |

La única diferencia está en la forma de cada celda de la tabla: en el **AFD** el destino es **un
estado** (`"q1"`) y en el **AFN** es un **conjunto de estados** (`["q0", "q1"]`). En el AFN, la
columna de transiciones vacías se escribe con la llave `"λ"` o `""`.

```jsonc
// POST /afd/evaluar
{
  "estado_inicial": "q0",
  "estados_finales": ["q2"],
  "tabla_transicion": { "q0": {"a": "q1"}, "q1": {"b": "q2"}, "q2": {} },
  "cadenas": ["ab", "aa"]
}

// POST /afn/evaluar
{
  "estado_inicial": "q0",
  "estados_finales": ["q2"],
  "tabla_transicion": { "q0": {"a": ["q0", "q1"], "λ": ["q1"]}, "q1": {"b": ["q2"]}, "q2": {} },
  "cadenas": ["aab", ""]
}
```

### Datos de salida

Cada respuesta incluye lo que pide la actividad:

| Campo | Descripción |
|---|---|
| `estados_totales`, `numero_de_estados` | $Q$, deducido de la tabla de transición |
| `alfabeto` | $\Sigma$ (λ **no** forma parte del alfabeto) |
| `estado_inicial` | $q_0$ |
| `estados_finales` | $F$ |
| `resultados[]` | Una entrada por cadena evaluada |
| `resumen` | Listas de cadenas aceptadas y rechazadas |

Y dentro de cada entrada de `resultados[]`, la **notación de transición**:

| Campo | Ejemplo (AFD) | Ejemplo (AFN) |
|---|---|---|
| `pasos` | `δ(q0, a) = q1` | `δ({q0}, a) = {q0, q1}` |
| `configuraciones` | `(q0, ab) ⊢ (q1, b) ⊢ (q2, λ)` | `({q0}, ab) ⊢ ({q0,q1}, b) ⊢ ({q0,q2}, λ)` |
| `funcion_extendida` | `δ*(q0, ab) = q2` | `δ*({q0}, ab) = {q0, q2}` |
| `recorrido` / `camino_de_aceptacion` | `q0 --a--> q1 --b--> q2` | un camino concreto que acepta |
| `cerradura_inicial` | — | `cerradura-λ({q0}) = {q0, q1}` |

Además, `aceptada`, `estado_final_alcanzado` (AFD) / `estados_alcanzados` (AFN), `detalle_pasos`
en forma estructurada y `motivo`, que explica en texto por qué se aceptó o rechazó la cadena.

## Cómo correr el servicio

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload
```

Documentación interactiva en `http://127.0.0.1:8000/docs`.

Para reproducir el notebook (levanta y detiene el servidor por su cuenta):

```bash
.venv/bin/python -m jupyter notebook Actividad_6.ipynb
```

---

# Resultados de los ejercicios

Todos los resultados de abajo se obtuvieron **a través de los endpoints**, con las llamadas HTTP
que están en el notebook.

## Ejercicio 1 — AFD (`POST /afd/evaluar`)

AFD construido en JFLAP para el Reporte 1, sobre $\Sigma = \{a, b, c, d, e\}$. Es un AFD
**completo**; $q_9$ es el estado trampa (absorbente y no final), por lo que toda cadena que
contenga `e` se rechaza.

**Tabla de transición enviada al endpoint** (`->` inicial, `*` final):

| δ | a | b | c | d | e |
|---|---|---|---|---|---|
| -> q0 | q1 | q2 | q3 | q5 | q9 |
| q1 | q1 | q2 | q4 | q5 | q9 |
| \* q2 | q4 | q2 | q6 | q5 | q9 |
| q3 | q1 | q6 | q3 | q7 | q9 |
| \* q4 | q4 | q2 | q7 | q8 | q9 |
| q5 | q6 | q2 | q3 | q5 | q9 |
| \* q6 | q6 | q7 | q8 | q5 | q9 |
| \* q7 | q4 | q7 | q8 | q7 | q9 |
| \* q8 | q6 | q2 | q8 | q8 | q9 |
| q9 | q9 | q9 | q9 | q9 | q9 |

**Descripción del autómata que devolvió el endpoint:**

```
Tipo de automata : AFD   M = (Q, Σ, δ, q0, F)
Q  (estados)     : {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9}   -> 10 estados
Σ  (alfabeto)    : {a, b, c, d, e}
q0 (inicial)     : q0
F  (finales)     : {q2, q4, q6, q7, q8}
```

**Evaluación de las 15 cadenas:**

| Cadena | Resultado | Notación de transición (δ\*) |
|---|---|---|
| `aaaab` | **ACEPTADA** | δ\*(q0, aaaab) = q2 |
| `cac` | **ACEPTADA** | δ\*(q0, cac) = q4 |
| `b` | **ACEPTADA** | δ\*(q0, b) = q2 |
| `abccc` | **ACEPTADA** | δ\*(q0, abccc) = q8 |
| `ab` | **ACEPTADA** | δ\*(q0, ab) = q2 |
| `aac` | **ACEPTADA** | δ\*(q0, aac) = q4 |
| `cccc` | rechazada | δ\*(q0, cccc) = q3 |
| `e` | rechazada | δ\*(q0, e) = q9 |
| `aaccc` | **ACEPTADA** | δ\*(q0, aaccc) = q8 |
| `bbc` | **ACEPTADA** | δ\*(q0, bbc) = q6 |
| `d` | rechazada | δ\*(q0, d) = q5 |
| `cdddd` | **ACEPTADA** | δ\*(q0, cdddd) = q7 |
| `ad` | rechazada | δ\*(q0, ad) = q5 |
| `bbd` | rechazada | δ\*(q0, bbd) = q5 |
| `bbbbb` | **ACEPTADA** | δ\*(q0, bbbbb) = q2 |

**Aceptadas (10):** `aaaab`, `cac`, `b`, `abccc`, `ab`, `aac`, `aaccc`, `bbc`, `cdddd`, `bbbbb`
**Rechazadas (5):** `cccc`, `e`, `d`, `ad`, `bbd`

**Notación de transición completa de tres casos representativos:**

```
Cadena: 'abccc'  ->  ACEPTADA
    δ(q0, a) = q1
    δ(q1, b) = q2
    δ(q2, c) = q6
    δ(q6, c) = q8
    δ(q8, c) = q8
  Configuraciones:    (q0, abccc) ⊢ (q1, bccc) ⊢ (q2, ccc) ⊢ (q6, cc) ⊢ (q8, c) ⊢ (q8, λ)
  Funcion extendida:  δ*(q0, abccc) = q8
  Recorrido:          q0 --a--> q1 --b--> q2 --c--> q6 --c--> q8 --c--> q8
  Motivo: la cadena se consumio por completo y termino en 'q8', que SI es un estado final.

Cadena: 'cccc'  ->  RECHAZADA
    δ(q0, c) = q3
    δ(q3, c) = q3
    δ(q3, c) = q3
    δ(q3, c) = q3
  Configuraciones:    (q0, cccc) ⊢ (q3, ccc) ⊢ (q3, cc) ⊢ (q3, c) ⊢ (q3, λ)
  Funcion extendida:  δ*(q0, cccc) = q3
  Motivo: termino en 'q3', que NO es un estado final.

Cadena: 'e'  ->  RECHAZADA
    δ(q0, e) = q9
  Configuraciones:    (q0, e) ⊢ (q9, λ)
  Funcion extendida:  δ*(q0, e) = q9
  Motivo: termino en 'q9' (estado trampa), que NO es un estado final.
```

## Ejercicio 2 — AFN (`POST /afn/evaluar`)

AFN de la Actividad 5, sobre $\Sigma = \{a, b, c\}$, que reconoce

$$L = \{w \in \{a,b,c\}^* : w \text{ termina en } abc \text{ o en } acb\}$$

El no determinismo está en $q_0$: con `a` el autómata puede quedarse en $q_0$ (seguir consumiendo
prefijo) **o** pasar a $q_1$ (apostar a que ahí empieza el sufijo).

**Tabla de transición enviada al endpoint:**

| δ | a | b | c |
|---|---|---|---|
| -> q0 | {q0, q1} | {q0} | {q0} |
| q1 | — | {q2} | {q3} |
| q2 | — | — | {q4} |
| q3 | — | {q5} | — |
| \* q4 | — | — | — |
| \* q5 | — | — | — |

**Descripción del autómata que devolvió el endpoint:**

```
Tipo de automata : AFN   M = (Q, Σ, δ, q0, F)  con  δ: Q × (Σ ∪ {λ}) → P(Q)
Q  (estados)     : {q0, q1, q2, q3, q4, q5}   -> 6 estados
Σ  (alfabeto)    : {a, b, c}
q0 (inicial)     : q0
F  (finales)     : {q4, q5}
Transiciones λ   : no
```

**Evaluación de las cadenas:**

| Cadena | Resultado | Notación de transición (δ\*) |
|---|---|---|
| `abc` | **ACEPTADA** | δ\*({q0}, abc) = {q0, q4} |
| `acb` | **ACEPTADA** | δ\*({q0}, acb) = {q0, q5} |
| `aabc` | **ACEPTADA** | δ\*({q0}, aabc) = {q0, q4} |
| `bcacb` | **ACEPTADA** | δ\*({q0}, bcacb) = {q0, q5} |
| `abcb` | rechazada | δ\*({q0}, abcb) = {q0} |
| `cba` | rechazada | δ\*({q0}, cba) = {q0, q1} |
| `λ` (cadena vacía) | rechazada | δ\*({q0}, λ) = {q0} |
| `a` | rechazada | δ\*({q0}, a) = {q0, q1} |
| `abcabc` | **ACEPTADA** | δ\*({q0}, abcabc) = {q0, q4} |
| `ccacb` | **ACEPTADA** | δ\*({q0}, ccacb) = {q0, q5} |
| `ab` | rechazada | δ\*({q0}, ab) = {q0, q2} |

**Aceptadas (6):** `abc`, `acb`, `aabc`, `bcacb`, `abcabc`, `ccacb`
**Rechazadas (5):** `abcb`, `cba`, `λ`, `a`, `ab`

**Notación de transición completa de dos casos:**

```
Cadena: 'aabc'  ->  ACEPTADA
  cerradura-λ({q0}) = {q0}
    δ({q0}, a)      = {q0, q1}
    δ({q0, q1}, a)  = {q0, q1}
    δ({q0, q1}, b)  = {q0, q2}
    δ({q0, q2}, c)  = {q0, q4}
  Configuraciones:       ({q0}, aabc) ⊢ ({q0,q1}, abc) ⊢ ({q0,q1}, bc) ⊢ ({q0,q2}, c) ⊢ ({q0,q4}, λ)
  Funcion extendida:     δ*({q0}, aabc) = {q0, q4}
  Camino de aceptacion:  q0 --a--> q0 --a--> q1 --b--> q2 --c--> q4
  Motivo: el conjunto alcanzado {q0, q4} contiene al estado final q4, asi que existe al menos un
          camino de aceptacion.

Cadena: 'ab'  ->  RECHAZADA
  cerradura-λ({q0}) = {q0}
    δ({q0}, a)      = {q0, q1}
    δ({q0, q1}, b)  = {q0, q2}
  Configuraciones:    ({q0}, ab) ⊢ ({q0,q1}, b) ⊢ ({q0,q2}, λ)
  Funcion extendida:  δ*({q0}, ab) = {q0, q2}
  Motivo: ninguno de los estados alcanzados es final (q2 esta a un simbolo de serlo, pero la
          cadena se acaba antes).
```

En el paso 3 de `aabc` se ve el no determinismo: desde $\{q_0, q_1\}$ el símbolo `b` lleva
simultáneamente a $q_0$ (rama que sigue leyendo prefijo) y a $q_2$ (rama que ya va a mitad del
sufijo `abc`). El AFD acepta si su **único** recorrido termina en estado final; el AFN acepta si
**existe al menos un** recorrido que lo haga.

## Ejercicio 3 — AFN con transiciones λ (`POST /afn/evaluar`)

AFN-λ que reconoce $a^{*}b^{*}c^{*}$. Sirve para ejercitar la **cerradura-λ** del evaluador: las
transiciones λ permiten pasar del bloque de las `a` al de las `b` y al de las `c` sin consumir
ningún símbolo.

**Tabla de transición enviada al endpoint:**

| δ | a | b | c | λ |
|---|---|---|---|---|
| -> q0 | {q0} | — | — | {q1} |
| q1 | — | {q1} | — | {q2} |
| \* q2 | — | — | {q2} | — |

**Descripción del autómata que devolvió el endpoint:**

```
Tipo de automata : AFN-λ   M = (Q, Σ, δ, q0, F)  con  δ: Q × (Σ ∪ {λ}) → P(Q)
Q  (estados)     : {q0, q1, q2}   -> 3 estados
Σ  (alfabeto)    : {a, b, c}
q0 (inicial)     : q0
F  (finales)     : {q2}
Transiciones λ   : si
```

Nótese que `λ` **no** aparece en Σ, como corresponde a la definición formal.

**Evaluación de las cadenas:**

| Cadena | Resultado | Notación de transición (δ\*) |
|---|---|---|
| `λ` (cadena vacía) | **ACEPTADA** | δ\*({q0}, λ) = {q0, q1, q2} |
| `abc` | **ACEPTADA** | δ\*({q0}, abc) = {q2} |
| `aabbcc` | **ACEPTADA** | δ\*({q0}, aabbcc) = {q2} |
| `ac` | **ACEPTADA** | δ\*({q0}, ac) = {q2} |
| `b` | **ACEPTADA** | δ\*({q0}, b) = {q1, q2} |
| `ccc` | **ACEPTADA** | δ\*({q0}, ccc) = {q2} |
| `ba` | rechazada | δ\*({q0}, ba) = {} |
| `cba` | rechazada | δ\*({q0}, cba) = {} |
| `aaa` | **ACEPTADA** | δ\*({q0}, aaa) = {q0, q1, q2} |

**Aceptadas (7):** `λ`, `abc`, `aabbcc`, `ac`, `b`, `ccc`, `aaa`
**Rechazadas (2):** `ba`, `cba`

**Notación de transición completa de tres casos:**

```
Cadena: 'λ'  ->  ACEPTADA
  cerradura-λ({q0}) = {q0, q1, q2}
  (no hay pasos: no se consume ningun simbolo)
  Configuraciones:       ({q0, q1, q2}, λ)
  Funcion extendida:     δ*({q0}, λ) = {q0, q1, q2}
  Camino de aceptacion:  q0 --λ--> q1 --λ--> q2

Cadena: 'ac'  ->  ACEPTADA
  cerradura-λ({q0}) = {q0, q1, q2}
    δ({q0, q1, q2}, a) = {q0}  →  cerradura-λ = {q0, q1, q2}
    δ({q0, q1, q2}, c) = {q2}
  Configuraciones:       ({q0,q1,q2}, ac) ⊢ ({q0,q1,q2}, c) ⊢ ({q2}, λ)
  Funcion extendida:     δ*({q0}, ac) = {q2}
  Camino de aceptacion:  q0 --a--> q0 --λ--> q1 --λ--> q2 --c--> q2

Cadena: 'ba'  ->  RECHAZADA
  cerradura-λ({q0}) = {q0, q1, q2}
    δ({q0, q1, q2}, b) = {q1}  →  cerradura-λ = {q1, q2}
    δ({q1, q2}, a)     = {}
  Configuraciones:    ({q0,q1,q2}, ba) ⊢ ({q1,q2}, a) ⊢ ({}, λ)
  Funcion extendida:  δ*({q0}, ba) = {}
  Motivo: el conjunto de estados alcanzables quedo vacio; una vez cruzada la λ-transicion a q1 ya
          no hay manera de volver a leer una 'a'.
```

Sin la cerradura-λ la cadena vacía sería rechazada, y este autómata sí la acepta.

## Casos borde y validación

| Caso | Respuesta del servicio |
|---|---|
| AFD con tabla **incompleta** (`{"q0": {"a": "q1"}, ...}`, cadena `aa`) | `200` — rechazada, `δ*(q0, aa) = indefinida`, motivo: *no existe la transición δ(q1, a); el AFD se detiene en el símbolo 2* (equivale a caer en un estado trampa) |
| Estado inicial que no aparece en la tabla | `400` — *El estado inicial 'qX' no aparece en el automata.* |
| Estado final que no aparece en la tabla | `400` — *Estados finales que no aparecen en el automata: ['q9']* |
| Tabla **no determinista** enviada a `/afd/evaluar` | `422` — *Input should be a valid string* (Pydantic rechaza la lista y obliga a usar `/afn/evaluar`) |

Los estados totales se deducen **únicamente** de la tabla de transición (renglones y destinos),
nunca del estado inicial ni de los finales; por eso un estado mal escrito se detecta en lugar de
agregarse silenciosamente al autómata.

## Conclusiones

* Los dos evaluadores comparten la lectura de la tabla de transición —de ahí salen $Q$ y
  $\Sigma$— pero difieren en la simulación: el AFD mantiene **un estado actual** y el AFN mantiene
  un **conjunto de estados actuales**, que es la construcción de subconjuntos aplicada sobre la
  marcha.
* La forma de la tabla basta para distinguir los dos autómatas: una celda con un estado (AFD)
  contra una celda con un conjunto de estados (AFN).
* Un AFD acepta una cadena si su único recorrido termina en un estado final; un AFN la acepta si
  existe al menos un recorrido que lo haga, aunque otras ramas mueran o terminen en estados no
  finales.
* Las transiciones λ no agregan poder de reconocimiento, pero obligan a calcular la cerradura-λ
  antes y después de cada símbolo.

## Archivos del repositorio

| Archivo | Contenido |
|---|---|
| [`main.py`](./main.py) | Servicio FastAPI con los endpoints `/afd/evaluar` y `/afn/evaluar` |
| [`Actividad_6.ipynb`](./Actividad_6.ipynb) | Desarrollo documentado con las llamadas reales a los endpoints |
| [`automatas.json`](./automatas.json) | Definición de los tres autómatas y sus cadenas de prueba |
| [`requirements.txt`](./requirements.txt) | Dependencias |
