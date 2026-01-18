# Bingo_P

Aplicacion para gestionar partidas de bingo con palabras en lugar de numeros.

## Funcionamiento del Juego

### Descripcion General

Bingo_P es una variante del bingo tradicional donde en lugar de numeros se utilizan palabras en diferentes idiomas. Los jugadores tienen cartones con palabras y gana el primero que complete todas las palabras de su carton.

### Flujo de una Partida

1. **Carga de Cartones**: Se cargan los cartones desde archivo o se ingresan manualmente
2. **Inicio de Partida**: El sistema genera un orden aleatorio de rondas (una por idioma)
3. **Desarrollo de Rondas**: Por cada ronda:
   - Se extraen palabras aleatorias del repositorio del idioma actual
   - El sistema marca automaticamente los cartones que contienen la palabra
   - La ronda termina cuando hay un ganador o se alcanza el limite de extracciones
4. **Avance**: Se continua con la siguiente ronda hasta completar los 4 idiomas
5. **Fin**: La partida termina cuando se completan todas las rondas

### Deteccion de Ganador

Un carton gana cuando todas sus palabras han sido marcadas. El sistema utiliza un indice invertido que mapea cada palabra a los cartones que la contienen, permitiendo detectar ganadores en tiempo O(k) donde k es el numero de cartones afectados por la palabra anunciada.

### Limite de Extracciones

Para garantizar probabilidades justas de ganar, cada ronda tiene un limite de extracciones calculado en funcion del tamaño del repositorio:

```
minimo = max_palabras * 3
maximo = total_repositorio * 0.8
limite = max(minimo, maximo)
```

El limite se basa en un porcentaje (80%) del repositorio disponible para el idioma, garantizando que se extraigan suficientes palabras para que los cartones tengan oportunidad real de ganar. El minimo de 3 veces las palabras del carton asegura una cobertura base incluso con repositorios pequeños.

Si se alcanza el limite sin ganador, la ronda termina sin ganador y se avanza a la siguiente.

## Estructura del Proyecto

```
Bingo_P/
├── constantes.py      # Configuracion de idiomas y rutas
├── algoritmos.py      # Algoritmos DyC y DP
├── carton.py          # Clase Carton (entidad)
├── repositorio.py     # Clase RepositorioPalabras
├── gestor.py          # Clase GestorBingo (logica del juego)
├── bingo_p.py         # Modulo principal (API publica)
├── gui.py             # Interfaz grafica (Tkinter)
├── repositorio/       # Palabras por idioma
│   ├── palabras_SP.txt
│   ├── palabras_EN.txt
│   ├── palabras_PT.txt
│   └── palabras_DT.txt
└── cartones/          # Archivos de cartones
    └── cartones_ejemplo.txt
```

## Idiomas Soportados

| Codigo | Idioma    | Max Palabras/Carton |
|--------|-----------|---------------------|
| SP     | Español   | 24                  |
| EN     | Ingles    | 14                  |
| PT     | Portugues | 20                  |
| DT     | Dutch     | 10                  |

## Ejecucion

```bash
cd Bingo_P
python3 gui.py
```

## Formato de Cartones

```
CARD_ID PLAYER_ID palabra1 palabra2 palabra3 ...
```

Ejemplo:
```
SP000001 J001 casa perro gato mesa silla
EN000001 J002 house dog cat table chair
```

- `CARD_ID`: 8 caracteres (2 letras idioma + 6 digitos)
- `PLAYER_ID`: Opcional (letra + digitos, ej: J001)

## Estrategias Algoritmicas

El proyecto utiliza tecnicas inspiradas en estrategias clasicas de diseno de algoritmos. Si bien las aplicaciones no son casos puros de estas estrategias, se aprovechan sus principios fundamentales para resolver problemas especificos del sistema.

### Diseño Original (Avance del Proyecto)

El diseño original presentado en el avance del proyecto se inspiro en los principios de Dividir y Conquistar y Programacion Dinamica:

**Inspiracion en Dividir y Conquistar:**
- **Particionamiento por idioma**: Los cartones se dividen en 4 particiones independientes (SP, EN, PT, DT). Cada ronda procesa unicamente su particion, reduciendo el espacio de trabajo. Esta separacion sigue el principio de dividir el problema en subproblemas mas pequenos y manejables.
- **Indice invertido particionado**: La estructura `indice_palabras[idioma][palabra]` divide el espacio de busqueda, permitiendo acceso directo a la particion relevante sin recorrer todo el conjunto de datos.

**Inspiracion en Programacion Dinamica:**
- **Contadores incrementales**: En lugar de recalcular si un carton es ganador verificando todas sus palabras en cada turno O(k), se mantiene un contador `aciertos` que se actualiza incrementalmente. Este enfoque se inspira en el principio de DP de almacenar resultados parciales para evitar recalculos.
- **Estado memoizado**: El estado de cada carton (palabras marcadas, aciertos) se mantiene actualizado, evitando recomputar el progreso desde cero.

### Implementacion Explicita de las Estrategias

Para demostrar de forma explicita el uso de estas estrategias, se implementaron algoritmos clasicos de DyC y DP fieles al texto guia CLRS:

### Dividir y Conquistar

La estrategia de Dividir y Conquistar (CLRS Cap. 2, Sec. 2.3, pag. 30) se basa en tres pasos: dividir el problema en subproblemas, conquistar resolviendolos recursivamente, y combinar las soluciones.

**Algoritmo MERGE (CLRS pag. 31):**

Se utiliza para combinar dos subarreglos ordenados en uno solo. Es el paso de "combinar" en Merge Sort.

```
MERGE(A, p, q, r)
1   n1 = q - p + 1
2   n2 = r - q
3   sean L[1..n1+1] y R[1..n2+1] nuevos arreglos
4   for i = 1 to n1
5       L[i] = A[p + i - 1]
6   for j = 1 to n2
7       R[j] = A[q + j]
8   L[n1 + 1] = infinito
9   R[n2 + 1] = infinito
10  i = 1
11  j = 1
12  for k = p to r
13      if L[i] <= R[j]
14          A[k] = L[i]
15          i = i + 1
16      else A[k] = R[j]
17          j = j + 1
```

**Algoritmo MERGE-SORT (CLRS pag. 34):**

Ordena el repositorio de palabras al momento de cargarlo. El ordenamiento permite posteriormente utilizar busqueda binaria para validaciones eficientes.

```
MERGE-SORT(A, p, r)
1   if p < r
2       q = floor((p + r) / 2)
3       MERGE-SORT(A, p, q)
4       MERGE-SORT(A, q + 1, r)
5       MERGE(A, p, q, r)
```

Complejidad: O(n log n) temporal, O(n) espacial.

**Algoritmo BUSQUEDA-BINARIA (CLRS Ejercicio 2.3-5, pag. 39):**

Se utiliza para verificar si una palabra existe en el repositorio ordenado. En cada paso se divide el espacio de busqueda a la mitad.

```
BUSQUEDA-BINARIA(A, p, r, v)
1   if p > r
2       return NIL
3   q = floor((p + r) / 2)
4   if A[q] == v
5       return q
6   else if v < A[q]
7       return BUSQUEDA-BINARIA(A, p, q - 1, v)
8   else
9       return BUSQUEDA-BINARIA(A, q + 1, r, v)
```

Complejidad: O(log n) temporal, O(log n) espacial (pila de recursion).

### Programacion Dinamica

La Programacion Dinamica (CLRS Cap. 15, pag. 359) se aplica a problemas con subestructura optima y subproblemas superpuestos, almacenando resultados en una tabla para evitar recalculos.

**Algoritmo DISTANCIA-EDICION (CLRS Problema 15-5, pags. 406-407):**

Se utiliza para sugerir correcciones cuando el usuario ingresa palabras con errores tipograficos. El algoritmo calcula el minimo numero de operaciones (insertar, eliminar, reemplazar) para transformar una cadena en otra.

La recurrencia que define el problema es:

```
c[i, 0] = i                              para i = 0, 1, ..., m
c[0, j] = j                              para j = 0, 1, ..., n
c[i, j] = c[i-1, j-1]                    si X[i] == Y[j]
c[i, j] = 1 + min(c[i-1, j],             eliminar
                  c[i, j-1],             insertar
                  c[i-1, j-1])           reemplazar, si X[i] != Y[j]
```

Pseudocodigo:

```
DISTANCIA-EDICION(X, Y)
1   m = length(X)
2   n = length(Y)
3   sea c[0..m, 0..n] una nueva tabla
4   for i = 0 to m
5       c[i, 0] = i
6   for j = 0 to n
7       c[0, j] = j
8   for i = 1 to m
9       for j = 1 to n
10          if X[i] == Y[j]
11              c[i, j] = c[i-1, j-1]
12          else
13              c[i, j] = 1 + min(c[i-1, j], c[i, j-1], c[i-1, j-1])
14  return c[m, n]
```

Complejidad: O(m * n) temporal, O(m * n) espacial.

**Justificacion:** La distancia de edicion es un problema clasico de DP con:
- **Subproblemas superpuestos**: El calculo de c[i,j] depende de c[i-1,j-1], c[i-1,j] y c[i,j-1], celdas calculadas previamente.
- **Subestructura optima**: La solucion optima para transformar X[1..i] en Y[1..j] se construye a partir de soluciones optimas de los subproblemas.

### Otras Tecnicas Utilizadas

Ademas de DyC y DP, el proyecto utiliza:

- **Indice Invertido**: Estructura de datos que mapea cada palabra a la lista de cartones que la contienen. Permite encontrar cartones afectados en O(1). Referencia: CLRS Cap. 11, Hash Tables.

- **Tablas Hash**: Los diccionarios de Python implementan hash tables para acceso O(1) a cartones por ID y palabras por idioma. Referencia: CLRS Cap. 11, pags. 253-285.

- **Particionamiento de Datos**: Los cartones se organizan por idioma, reduciendo el espacio de busqueda en cada ronda.

## Modulos

### constantes.py
Define la configuracion global del sistema.

### algoritmos.py
Contiene los algoritmos de Dividir y Conquistar y Programacion Dinamica fieles a CLRS:
- `merge(A, p, q, r)` - CLRS pag. 31
- `merge_sort(A, p, r)` - CLRS pag. 34
- `busqueda_binaria(A, p, r, v)` - CLRS Ejercicio 2.3-5, pag. 39
- `distancia_edicion(X, Y)` - CLRS Problema 15-5, pags. 406-407

### carton.py
Define la clase `Carton` con:
- Propiedades: id, idioma, palabras, jugador_id, aciertos
- Metodos: marcar_palabra(), reiniciar(), es_ganador

### repositorio.py
Gestiona las palabras disponibles por idioma:
- Carga y ordena palabras usando Merge Sort
- Valida existencia usando Busqueda Binaria
- Sugiere correcciones usando Distancia de Edicion

### gestor.py
Controla la logica del juego:
- Gestion de cartones (agregar, validar, cargar desde archivo)
- Control de partidas (iniciar, anunciar palabra, avanzar ronda)
- Indice invertido para busqueda eficiente palabra -> cartones

### bingo_p.py
Modulo principal que re-exporta toda la API publica.

## Complejidades

| Operacion | Algoritmo | Tiempo | Espacio |
|-----------|-----------|--------|---------|
| Ordenar repositorio | Merge Sort | O(n log n) | O(n) |
| Validar palabra | Busqueda Binaria | O(log n) | O(log n) |
| Sugerir correccion | Distancia Edicion | O(m * n) | O(m * n) |
| Anunciar palabra | Indice Invertido | O(c) | O(1) |

Donde:
- n = palabras en repositorio
- m, n = longitud de las cadenas comparadas
- c = cartones que contienen la palabra anunciada

## Referencias

[1] T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein, *Introduction to Algorithms*, 3rd ed. Cambridge, MA, USA: MIT Press, 2009.
- Seccion 2.3: Designing algorithms (Merge Sort), pags. 30-37
- Ejercicio 2.3-5: Binary Search, pag. 39
- Capitulo 11: Hash Tables, pags. 253-285
- Capitulo 15: Dynamic Programming, pags. 359-410
- Problema 15-5: Edit Distance, pags. 406-407

## Integrantes

- Victor Morales
- Andres Saltos
- Darwin Diaz
- Juliana Burgos
- Gabriel Tumbaco

Curso: Analisis de Algoritmos II PAO 2025 - Paralelo 2 - Grupo 2
