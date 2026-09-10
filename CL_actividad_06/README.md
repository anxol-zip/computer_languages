# Actividad 6 — Implementación de un evaluador de cadenas para un AFD y un AFN

**Materia:** Lenguajes de Computación · Otoño 2026

## Identificación del equipo

| Nombre completo | No. de cuenta |
|---|---|
| Angel Rugerio Jiménez | 201720 |
| Axel García Arellano | 201251 |

**Nombre de la actividad:** Actividad 6 — Implementación de evaluador de cadenas para un AFD y un AFN.

---

## Descripción

Servicio web hecho con [FastAPI](https://fastapi.tiangolo.com/) ([`main.py`](./main.py)) con
**un endpoint por evaluador**: uno para autómatas finitos deterministas y otro para autómatas
finitos no deterministas.

El desarrollo completo, con las llamadas reales a los endpoints, está en
[`Actividad_6.ipynb`](./Actividad_6.ipynb). Los dos autómatas que se evalúan están en
[`automatas.json`](./automatas.json) y son los que ya habíamos trabajado a mano: el AFD del
**Reporte 1** y el AFN de la **Actividad 5**, con las mismas cadenas, para poder comprobar que el
evaluador da lo mismo que salió en papel.

## Endpoints

| Endpoint | Método | Autómata | Transición |
|---|---|---|---|
| `/` | GET | — | Información del servicio |
| `/afd/evaluar` | POST | Determinista | $\delta: Q \times \Sigma \to Q$ |
| `/afn/evaluar` | POST | No determinista | $\Delta: Q \times (\Sigma \cup \{\varepsilon\}) \to \mathcal{P}(Q)$ |

### Parámetros de entrada

Los dos endpoints reciben el mismo cuerpo JSON:

| Campo | Tipo | Descripción |
|---|---|---|
| `tabla_transicion` | objeto | `tabla[estado][símbolo] = destino` |
| `estado_inicial` | cadena | $s$ |
| `estados_finales` | lista | $F$ |
| `cadenas` | lista | Cadena(s) a evaluar |

La única diferencia está en la forma de cada celda: en el **AFD** el destino es **un estado**
(`"q1"`) y en el **AFN** es un **conjunto de estados** (`["q0", "q1"]`). En el AFN se puede
agregar una columna de transiciones vacías con la llave `"ε"` o `""`.

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
  "tabla_transicion": { "q0": {"a": ["q0", "q1"], "b": ["q0"]}, "q1": {"b": ["q2"]}, "q2": {} },
  "cadenas": ["aab", "ba"]
}
```

### Datos de salida

Cada respuesta trae lo que pide la actividad:

| Campo | Descripción |
|---|---|
| `estados_totales`, `numero_de_estados` | $Q$, deducido de la tabla de transición |
| `alfabeto` | $\Sigma$ (la transición vacía **no** forma parte del alfabeto) |
| `estado_inicial` | $s$ |
| `estados_finales` | $F$ |
| `resultados[]` | Una entrada por cadena evaluada |
| `resumen` | Listas de cadenas válidas e inválidas |

Y dentro de cada entrada de `resultados[]`, la **notación de transición**:

| Campo | Ejemplo (AFD) | Ejemplo (AFN) |
|---|---|---|
| `pasos` | `δ(q0, a) = q1` | `Δ({q0}, a) = {q0, q1}` |
| `recorrido` / `camino_de_aceptacion` | `q0 --a--> q1 --b--> q2` | un recorrido concreto que acepta |

Además `aceptada`, `estado_final_alcanzado` (AFD) / `configuracion_final` (AFN) y `motivo`, que
explica en texto por qué se aceptó o se rechazó la cadena.

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

Todo lo de abajo se obtuvo **a través de los endpoints**, con las llamadas HTTP que están en el
notebook.

## Ejercicio 1 — AFD (`POST /afd/evaluar`)

AFD del **Reporte 1**, sobre $\Sigma = \{a, b, c, d, e\}$. Es un AFD **completo**: hay exactamente
una transición por cada par (estado, símbolo). $q_9$ es el estado trampa (absorbente y no final),
así que toda cadena que contenga `e` se rechaza.

**Tabla de transición que se envía al endpoint** (`->` inicial, `*` final):

```
δ   ->q0   q1     *q2    q3     *q4    q5     *q6    *q7    *q8    q9
--------------------------------------------------------------------------
a   q1     q1     q4     q1     q4     q6     q6     q4     q6     q9
b   q2     q2     q2     q6     q2     q2     q7     q7     q2     q9
c   q3     q4     q6     q3     q7     q3     q8     q8     q8     q9
d   q5     q5     q5     q7     q8     q5     q5     q7     q8     q9
e   q9     q9     q9     q9     q9     q9     q9     q9     q9     q9
```

**Descripción del autómata que devolvió el endpoint:**

```
Tipo : AFD   A = (Q, Σ, δ, s, F)  con  δ: Q × Σ → Q
Q    : {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9}   -> 10 estados
Σ    : {a, b, c, d, e}
s    : q0
F    : {q2, q4, q6, q7, q8}
```

Coincide con los componentes que habíamos identificado en el Reporte 1.

**Evaluación de las 15 cadenas:**

| Cadena | Resultado | Termina en |
|---|---|---|
| `aaaab` | **Válida** | q2 |
| `cac` | **Válida** | q4 |
| `b` | **Válida** | q2 |
| `abccc` | **Válida** | q8 |
| `ab` | **Válida** | q2 |
| `aac` | **Válida** | q4 |
| `cccc` | Inválida | q3 |
| `e` | Inválida | q9 |
| `aaccc` | **Válida** | q8 |
| `bbc` | **Válida** | q6 |
| `d` | Inválida | q5 |
| `cdddd` | **Válida** | q7 |
| `ad` | Inválida | q5 |
| `bbd` | Inválida | q5 |
| `bbbbb` | **Válida** | q2 |

**Válidas (10):** `aaaab`, `cac`, `b`, `abccc`, `ab`, `aac`, `aaccc`, `bbc`, `cdddd`, `bbbbb`
**Inválidas (5):** `cccc`, `e`, `d`, `ad`, `bbd`

Es el mismo veredicto de las 15 cadenas que salió a mano en el Reporte 1.

**Notación de transición de tres casos representativos:**

```
Cadena 'abccc'  ->  ACEPTADA

    δ(q0, a) = q1
    δ(q1, b) = q2
    δ(q2, c) = q6
    δ(q6, c) = q8
    δ(q8, c) = q8

    Recorrido:  q0 --a--> q1 --b--> q2 --c--> q6 --c--> q8 --c--> q8

    La cadena se consumio por completo y termino en 'q8', que SI es un estado final.


Cadena 'cccc'  ->  RECHAZADA

    δ(q0, c) = q3
    δ(q3, c) = q3
    δ(q3, c) = q3
    δ(q3, c) = q3

    Recorrido:  q0 --c--> q3 --c--> q3 --c--> q3 --c--> q3

    La cadena se consumio por completo y termino en 'q3', que NO es un estado final.


Cadena 'e'  ->  RECHAZADA

    δ(q0, e) = q9

    Recorrido:  q0 --e--> q9

    La cadena se consumio por completo y termino en 'q9', que NO es un estado final.
```

En el último caso `q9` es el estado trampa: es absorbente, así que una vez que se cae ahí ya no
hay manera de volver a un estado final.

## Ejercicio 2 — AFN (`POST /afn/evaluar`)

AFN de la **Actividad 5**, sobre $\Sigma = \{a, b, c\}$. El no determinismo está en $q_0$: al leer
`a` el autómata **se queda en $q_0$ y a la vez pasa a $q_1$**, es decir
$\Delta(q_0, a) = \{q_0, q_1\}$. La rama que se queda sigue leyendo prefijo y la que salta a $q_1$
apuesta a que ahí empieza el sufijo.

**Tabla de transición que se envía al endpoint:**

```
Δ   ->q0      q1        q2        q3        *q4       *q5
----------------------------------------------------------------
a   {q0,q1}   Φ         Φ         Φ         Φ         Φ
b   {q0}      {q2}      Φ         {q5}      Φ         Φ
c   {q0}      {q3}      {q4}      Φ         Φ         Φ
```

Nótese que la celda ya no es un estado sino un **conjunto**, y que hay celdas vacías ($\Phi$),
algo imposible en un AFD completo.

**Descripción del autómata que devolvió el endpoint:**

```
Tipo : AFN   A = (Q, Σ, Δ, s, F)  con  Δ: Q × (Σ ∪ {ε}) → P(Q)
Q    : {q0, q1, q2, q3, q4, q5}   -> 6 estados
Σ    : {a, b, c}
s    : q0
F    : {q4, q5}
```

**Evaluación de las 9 cadenas de la Actividad 5:**

La columna "termina en" ya no es un estado sino la **configuración final**: el conjunto de estados
en los que el autómata podría estar al acabar la cadena. Se acepta si ese conjunto toca a $F$.

| Cadena | Resultado | Configuración final |
|---|---|---|
| `abc` | **Válida** | {q0, q4} |
| `acb` | **Válida** | {q0, q5} |
| `ab` | Inválida | {q0, q2} |
| `ac` | Inválida | {q0, q3} |
| `cbaacb` | **Válida** | {q0, q5} |
| `bbabc` | **Válida** | {q0, q4} |
| `abca` | Inválida | {q0, q1} |
| `abcb` | Inválida | {q0} |
| `accb` | Inválida | {q0} |

**Válidas (4):** `abc`, `acb`, `cbaacb`, `bbabc`
**Inválidas (5):** `ab`, `ac`, `abca`, `abcb`, `accb`

Es el mismo veredicto que salió al trazar las ramas a mano en la Actividad 5.

**Notación de transición de tres casos:**

```
Cadena 'abc'  ->  ACEPTADA

    Δ({q0}, a) = {q0, q1}
    Δ({q0, q1}, b) = {q0, q2}
    Δ({q0, q2}, c) = {q0, q4}

    Recorrido:  q0 --a--> q1 --b--> q2 --c--> q4

    La configuracion final es {q0, q4} y contiene {q4} de F, asi que existe al menos un
    recorrido que acepta la cadena.


Cadena 'cbaacb'  ->  ACEPTADA

    Δ({q0}, c) = {q0}
    Δ({q0}, b) = {q0}
    Δ({q0}, a) = {q0, q1}
    Δ({q0, q1}, a) = {q0, q1}
    Δ({q0, q1}, c) = {q0, q3}
    Δ({q0, q3}, b) = {q0, q5}

    Recorrido:  q0 --c--> q0 --b--> q0 --a--> q0 --a--> q1 --c--> q3 --b--> q5

    La configuracion final es {q0, q5} y contiene {q5} de F, asi que existe al menos un
    recorrido que acepta la cadena.


Cadena 'abcb'  ->  RECHAZADA

    Δ({q0}, a) = {q0, q1}
    Δ({q0, q1}, b) = {q0, q2}
    Δ({q0, q2}, c) = {q0, q4}
    Δ({q0, q4}, b) = {q0}

    La configuracion final es {q0} y ninguno de esos estados es final.
```

En `abcb` se ve la diferencia con el AFD: la rama buena llega a $q_4$ pero ahí se le acaba la
salida (esa rama muere, $\Phi$) y la única que sobrevive es la que se quedó dando vueltas en
$q_0$, que no es final. El AFD acepta si su **único** recorrido termina en estado final; el AFN
acepta si **existe al menos un** recorrido que lo haga.

## Casos borde y validación

| Caso | Respuesta del servicio |
|---|---|
| AFD con tabla **incompleta** (`{"q0": {"a": "q1"}, ...}`, cadena `aa`) | `200` — inválida, motivo: *no existe la transición δ(q1, a); el AFD se detiene en el símbolo 2* (equivale a caer en un estado trampa) |
| Estado inicial que no aparece en la tabla | `400` — *El estado inicial 'qX' no aparece en el automata.* |
| Estado final que no aparece en la tabla | `400` — *Estados finales que no aparecen en el automata: ['q9']* |
| Tabla **no determinista** enviada a `/afd/evaluar` | `422` — *Input should be a valid string* (Pydantic rechaza la lista y obliga a usar `/afn/evaluar`) |

Los estados totales se deducen **únicamente** de la tabla de transición (renglones y destinos),
nunca del estado inicial ni de los finales; por eso un estado mal escrito se detecta en lugar de
agregarse en silencio al autómata.

## Conclusiones

* Los dos evaluadores comparten la lectura de la tabla de transición —de ahí salen $Q$ y
  $\Sigma$— pero difieren en la simulación: el AFD mantiene **un estado actual** y el AFN mantiene
  una **configuración**, o sea un conjunto de estados activos.
* La forma de la tabla basta para distinguir los dos autómatas: una celda con un estado (AFD)
  contra una celda con un conjunto de estados (AFN). Por eso el endpoint de AFD puede rechazar
  solo una tabla no determinista.
* Un AFD acepta una cadena si su único recorrido termina en un estado final; un AFN la acepta si
  existe al menos un recorrido que lo haga, aunque las otras ramas mueran o terminen en estados no
  finales.
* Los dos ejercicios dan exactamente el mismo veredicto que ya habíamos sacado a mano en el
  Reporte 1 y en la Actividad 5, que era el punto de comprobación.

## Archivos del repositorio

| Archivo | Contenido |
|---|---|
| [`main.py`](./main.py) | Servicio FastAPI con los endpoints `/afd/evaluar` y `/afn/evaluar` |
| [`Actividad_6.ipynb`](./Actividad_6.ipynb) | Desarrollo documentado con las llamadas reales a los endpoints |
| [`automatas.json`](./automatas.json) | Definición de los dos autómatas y sus cadenas |
| [`requirements.txt`](./requirements.txt) | Dependencias |
