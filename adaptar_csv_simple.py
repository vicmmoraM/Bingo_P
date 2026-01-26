"""
================================================================================
ADAPTADOR DE DATOS PARA BINGO_P
================================================================================

Autores:
    - Victor Morales
    - Andres Saltos
    - Darwin Diaz
    - Juliana Burgos
    - Gabriel Tumbaco

Curso: Análisis de Algoritmos II PAO 2025 - Paralelo 2 - Grupo 2

Descripción:
    Convierte el archivo CSV de frases a formato compatible con Bingo_P.
    Toma frases largas y extrae palabras individuales válidas del repositorio.

================================================================================
"""

import csv
from collections import Counter


ARCHIVO_ENTRADA = "datos_espanol.csv"  
ARCHIVO_SALIDA = "cartones_bingo.csv"  # Archivo procesado
REPOSITORIO = "repositorio/palabras_SP.txt"

# Palabras a ignorar (artículos, preposiciones, etc.)
PALABRAS_IGNORAR = {
    'el', 'la', 'los', 'las', 'un', 'una', 'al', 'del',
    'de', 'a', 'en', 'con', 'por', 'para', 'que', 'y', 'o',
}

MAX_PALABRAS = 24  # Máximo para español


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def cargar_repositorio(archivo):
    """
    Carga las palabras válidas del repositorio.
    
    Entrada:
        archivo (str): Ruta del archivo de palabras
    
    Salida:
        set: Conjunto de palabras válidas en minúsculas
    """
    palabras = set()
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            for linea in f:
                linea = linea.strip()
                if linea and not linea.startswith('#'):
                    palabras.add(linea.lower())
    except FileNotFoundError:
        print(f"⚠️  Archivo {archivo} no encontrado")
    return palabras


def extraer_palabras_validas(frase, repositorio):
    """
    Extrae palabras válidas de una frase.
    
    Proceso:
        1. Divide la frase en palabras
        2. Filtra palabras cortas (< 4 letras)
        3. Elimina artículos y preposiciones
        4. Valida contra el repositorio
    
    Entrada:
        frase (str): Frase completa
        repositorio (set): Palabras válidas
    
    Salida:
        list: Lista de palabras válidas extraídas
    """
    palabras = frase.lower().split()
    palabras_validas = []
    
    for palabra in palabras:
        # Limpiar puntuación
        palabra = palabra.strip('.,;:!?¿¡')
        
        # Filtros
        if len(palabra) < 4:  # Muy corta
            continue
        if palabra in PALABRAS_IGNORAR:  # Artículo/preposición
            continue
        if palabra not in repositorio:  # No está en repositorio
            continue
        
        palabras_validas.append(palabra)
    
    return palabras_validas


def seleccionar_mejores_palabras(palabras, max_palabras):
    """
    Selecciona las mejores palabras cuando hay más del máximo.
    
    Criterio:
        - Prioriza palabras únicas (elimina duplicados)
        - Prefiere palabras más largas
    
    Entrada:
        palabras (list): Lista de palabras válidas
        max_palabras (int): Cantidad máxima
    
    Salida:
        list: Lista de palabras seleccionadas
    """
    # Eliminar duplicados manteniendo orden
    palabras_unicas = list(dict.fromkeys(palabras))
    
    if len(palabras_unicas) <= max_palabras:
        return palabras_unicas
    
    # Ordenar por longitud (más largas primero)
    palabras_ordenadas = sorted(palabras_unicas, key=len, reverse=True)
    
    return palabras_ordenadas[:max_palabras]


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def procesar_csv():
    """
    Función principal que procesa el CSV de frases.
    
    Proceso completo:
        1. Cargar repositorio de palabras válidas
        2. Leer CSV de entrada línea por línea
        3. Extraer palabras de cada frase
        4. Seleccionar las mejores palabras (max 24)
        5. Generar CSV de salida compatible con Bingo_P
    """
    print("="*70)
    print(" ADAPTADOR DE DATOS PARA BINGO_P")
    print("="*70)
    
    # Paso 1: Cargar repositorio
    print("\n[1/4] Cargando repositorio de palabras válidas...")
    repositorio = cargar_repositorio(REPOSITORIO)
    print(f"      ✓ {len(repositorio)} palabras válidas cargadas")
    
    # Paso 2: Procesar CSV
    print(f"\n[2/4] Leyendo archivo: {ARCHIVO_ENTRADA}")
    
    cartones_procesados = []
    cartones_rechazados = 0
    
    try:
        with open(ARCHIVO_ENTRADA, 'r', encoding='utf-8') as f:
            lector = csv.reader(f)
            next(lector)  # Saltar encabezado
            
            for i, fila in enumerate(lector, 1):
                if len(fila) < 3:
                    continue
                
                id_carton = fila[0]
                usuario = fila[1]
                frase = fila[2]
                
                # Extraer palabras
                palabras = extraer_palabras_validas(frase, repositorio)
                
                if len(palabras) == 0:
                    cartones_rechazados += 1
                    continue
                
                # Seleccionar mejores palabras
                palabras_seleccionadas = seleccionar_mejores_palabras(
                    palabras, MAX_PALABRAS
                )
                
                cartones_procesados.append({
                    'id': id_carton,
                    'usuario': usuario,
                    'palabras': palabras_seleccionadas
                })
                
                # Mostrar progreso cada 100
                if i % 100 == 0:
                    print(f"      Procesando... {i} filas")
        
        print(f"      ✓ {len(cartones_procesados)} cartones procesados")
        print(f"      ✗ {cartones_rechazados} cartones rechazados (sin palabras válidas)")
        
    except FileNotFoundError:
        print(f"      ✗ ERROR: No se encontró {ARCHIVO_ENTRADA}")
        return
    
    # Paso 3: Generar estadísticas
    print(f"\n[3/4] Generando estadísticas...")
    
    todas_palabras = []
    for carton in cartones_procesados:
        todas_palabras.extend(carton['palabras'])
    
    contador = Counter(todas_palabras)
    palabras_unicas = len(contador)
    
    print(f"      • Palabras únicas usadas: {palabras_unicas}")
    print(f"      • Top 5 más frecuentes:")
    for palabra, freq in contador.most_common(5):
        print(f"        - {palabra}: {freq} veces")
    
    # Paso 4: Guardar resultado
    print(f"\n[4/4] Guardando en: {ARCHIVO_SALIDA}")
    
    with open(ARCHIVO_SALIDA, 'w', encoding='utf-8', newline='') as f:
        escritor = csv.writer(f)
        
        # Encabezado
        escritor.writerow(['CARD_ID', 'PLAYER_ID', 'PALABRAS'])
        
        # Datos
        for carton in cartones_procesados:
            fila = [carton['id'], carton['usuario']] + carton['palabras']
            escritor.writerow(fila)
    
    print(f"      ✓ Archivo generado exitosamente")
    
    # Resumen final
    print("\n" + "="*70)
    print(" RESUMEN")
    print("="*70)
    print(f"✅ Cartones procesados: {len(cartones_procesados)}")
    print(f"❌ Cartones rechazados: {cartones_rechazados}")
    print(f"📁 Archivo de salida: {ARCHIVO_SALIDA}")
    print(f"\n💡 Ahora puedes cargar '{ARCHIVO_SALIDA}' en Bingo_P")
    print("="*70 + "\n")
    
    # Mostrar ejemplo
    if cartones_procesados:
        print("📋 EJEMPLO DE CARTÓN PROCESADO:\n")
        ejemplo = cartones_procesados[0]
        print(f"   ID: {ejemplo['id']}")
        print(f"   Usuario: {ejemplo['usuario']}")
        print(f"   Palabras ({len(ejemplo['palabras'])}): {', '.join(ejemplo['palabras'])}")
        print()


# ============================================================================
# EJECUCIÓN
# ============================================================================

if __name__ == "__main__":
    procesar_csv()