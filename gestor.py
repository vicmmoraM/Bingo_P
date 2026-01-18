import random
from typing import Dict, List, Set, Optional, Tuple
from constantes import IDIOMAS
from carton import Carton
from repositorio import RepositorioPalabras


class GestorBingo:
    def __init__(self, repositorio: RepositorioPalabras = None):
        self._repositorio = repositorio
        self.cartones: Dict[str, Dict[str, Carton]] = {idioma: {} for idioma in IDIOMAS}
        self.indice_palabras: Dict[str, Dict[str, List[str]]] = {idioma: {} for idioma in IDIOMAS}
        self.orden_rondas: List[str] = list(IDIOMAS.keys())
        self.ronda_actual: int = 0
        self.palabras_anunciadas: Dict[str, List[str]] = {idioma: [] for idioma in IDIOMAS}
        self.ganadores: Dict[str, List[str]] = {idioma: [] for idioma in IDIOMAS}

    @property
    def repositorio(self) -> RepositorioPalabras:
        if self._repositorio is None:
            self._repositorio = RepositorioPalabras()
        return self._repositorio

    def validar_palabras_en_repositorio(self, idioma: str, palabras: Set[str]) -> Tuple[bool, List[str]]:
        palabras_invalidas = []
        for palabra in palabras:
            if not self.repositorio.palabra_existe(idioma, palabra):
                palabras_invalidas.append(palabra)
        return len(palabras_invalidas) == 0, palabras_invalidas

    def obtener_sugerencias(self, idioma: str, palabras_invalidas: List[str]) -> Dict[str, Optional[str]]:
        sugerencias = {}
        for palabra in palabras_invalidas:
            resultado = self.repositorio.sugerir_palabra(idioma, palabra)
            if resultado:
                sugerencias[palabra] = resultado[0]
            else:
                sugerencias[palabra] = None
        return sugerencias

    def validar_id_carton(self, id_carton: str) -> Tuple[bool, str]:
        if len(id_carton) != 8:
            return False, "El ID debe tener exactamente 8 caracteres"
        prefijo = id_carton[:2].upper()
        sufijo = id_carton[2:]
        if prefijo not in IDIOMAS:
            return False, f"Prefijo de idioma inválido: {prefijo}. Válidos: {list(IDIOMAS.keys())}"
        if not sufijo.isdigit():
            return False, "Los últimos 6 caracteres deben ser numéricos"
        return True, prefijo

    def agregar_carton(self, id_carton: str, palabras: List[str], jugador_id: str = "N/A") -> Tuple[bool, str]:
        es_valido, resultado = self.validar_id_carton(id_carton)
        if not es_valido:
            return False, resultado
        idioma = resultado
        id_carton = id_carton.upper()
        if id_carton in self.cartones[idioma]:
            return False, f"Ya existe un cartón con ID: {id_carton}"
        max_palabras = IDIOMAS[idioma]["max_palabras"]
        if len(palabras) > max_palabras:
            return False, f"El cartón excede el máximo de {max_palabras} palabras para {IDIOMAS[idioma]['nombre']}"
        palabras_normalizadas = {p.strip().lower() for p in palabras if p.strip()}
        todas_validas, palabras_invalidas = self.validar_palabras_en_repositorio(idioma, palabras_normalizadas)
        if not todas_validas:
            sugerencias = self.obtener_sugerencias(idioma, palabras_invalidas[:5])
            lineas = []
            for palabra in palabras_invalidas[:5]:
                sugerencia = sugerencias.get(palabra)
                if sugerencia:
                    lineas.append(f"  '{palabra}' -> ¿Quisiste decir '{sugerencia}'?")
                else:
                    lineas.append(f"  '{palabra}' (sin sugerencia)")
            mensaje = f"Palabras no encontradas en {IDIOMAS[idioma]['nombre']}:\n" + "\n".join(lineas)
            if len(palabras_invalidas) > 5:
                mensaje += f"\n  ... (+{len(palabras_invalidas)-5} más)"
            return False, mensaje
        carton = Carton(id=id_carton, idioma=idioma, palabras=palabras_normalizadas, jugador_id=jugador_id)
        self.cartones[idioma][id_carton] = carton
        for palabra in palabras_normalizadas:
            if palabra not in self.indice_palabras[idioma]:
                self.indice_palabras[idioma][palabra] = []
            self.indice_palabras[idioma][palabra].append(id_carton)
        return True, f"Cartón {id_carton} agregado correctamente"

    def _es_jugador_id(self, texto: str) -> bool:
        if len(texto) < 2:
            return False
        return texto[0].isalpha() and texto[1:].isdigit()

    def cargar_desde_archivo(self, ruta_archivo: str) -> Tuple[int, int, List[str]]:
        cargados = 0
        fallidos = 0
        errores = []
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                for num_linea, linea in enumerate(archivo, 1):
                    linea = linea.strip()
                    if not linea:
                        continue
                    partes = linea.split()
                    if len(partes) < 2:
                        errores.append(f"Línea {num_linea}: Formato inválido (se requiere ID y al menos 1 palabra)")
                        fallidos += 1
                        continue
                    id_carton = partes[0]
                    if len(partes) > 2 and self._es_jugador_id(partes[1]):
                        jugador_id = partes[1]
                        palabras = partes[2:]
                    else:
                        jugador_id = "N/A"
                        palabras = partes[1:]
                    if not palabras:
                        errores.append(f"Línea {num_linea}: Se requiere al menos 1 palabra")
                        fallidos += 1
                        continue
                    exito, mensaje = self.agregar_carton(id_carton, palabras, jugador_id)
                    if exito:
                        cargados += 1
                    else:
                        errores.append(f"Línea {num_linea}: {mensaje}")
                        fallidos += 1
        except FileNotFoundError:
            errores.append(f"Archivo no encontrado: {ruta_archivo}")
        except Exception as e:
            errores.append(f"Error al leer archivo: {str(e)}")
        return cargados, fallidos, errores

    def iniciar_partida(self):
        random.shuffle(self.orden_rondas)
        self.ronda_actual = 0
        for idioma in IDIOMAS:
            for carton in self.cartones[idioma].values():
                carton.reiniciar()
            self.palabras_anunciadas[idioma].clear()
            self.ganadores[idioma].clear()
        return self.orden_rondas.copy()

    def obtener_idioma_actual(self) -> Optional[str]:
        if self.ronda_actual < len(self.orden_rondas):
            return self.orden_rondas[self.ronda_actual]
        return None

    def anunciar_palabra(self, palabra: str) -> List[Carton]:
        idioma = self.obtener_idioma_actual()
        if idioma is None:
            return []
        palabra = palabra.strip().lower()
        self.palabras_anunciadas[idioma].append(palabra)
        nuevos_ganadores = []
        if palabra in self.indice_palabras[idioma]:
            ids_cartones = self.indice_palabras[idioma][palabra]
            for id_carton in ids_cartones:
                carton = self.cartones[idioma][id_carton]
                if not carton.es_ganador:
                    if carton.marcar_palabra(palabra):
                        if carton.es_ganador:
                            nuevos_ganadores.append(carton)
                            self.ganadores[idioma].append(id_carton)
        return nuevos_ganadores

    def calcular_limite_extracciones(self, idioma: str) -> int:
        max_palabras = IDIOMAS[idioma]["max_palabras"]
        total_repositorio = self.repositorio.obtener_total_palabras(idioma)
        minimo = max_palabras * 3
        maximo = int(total_repositorio * 0.8)
        return max(minimo, maximo)

    def limite_alcanzado(self) -> bool:
        idioma = self.obtener_idioma_actual()
        if idioma is None:
            return False
        limite = self.calcular_limite_extracciones(idioma)
        extracciones = len(self.palabras_anunciadas[idioma])
        return extracciones >= limite

    def obtener_extracciones_info(self) -> Tuple[int, int]:
        idioma = self.obtener_idioma_actual()
        if idioma is None:
            return 0, 0
        limite = self.calcular_limite_extracciones(idioma)
        extracciones = len(self.palabras_anunciadas[idioma])
        return extracciones, limite

    def avanzar_ronda(self) -> Tuple[bool, str]:
        self.ronda_actual += 1
        if self.ronda_actual >= len(self.orden_rondas):
            return False, "Todas las rondas han finalizado"
        nuevo_idioma = self.orden_rondas[self.ronda_actual]
        return True, f"Ronda de {IDIOMAS[nuevo_idioma]['nombre']}"

    def obtener_estadisticas(self) -> Dict:
        stats = {
            "total_cartones": sum(len(c) for c in self.cartones.values()),
            "por_idioma": {},
            "orden_rondas": [IDIOMAS[i]["nombre"] for i in self.orden_rondas],
            "ronda_actual": self.ronda_actual + 1 if self.ronda_actual < len(self.orden_rondas) else "Finalizado"
        }
        for idioma, cartones in self.cartones.items():
            stats["por_idioma"][IDIOMAS[idioma]["nombre"]] = {
                "cartones": len(cartones),
                "palabras_anunciadas": len(self.palabras_anunciadas[idioma]),
                "ganadores": len(self.ganadores[idioma])
            }
        return stats

    def obtener_estado_cartones(self, idioma: str = None) -> List[Dict]:
        resultado = []
        idiomas_a_revisar = [idioma] if idioma else IDIOMAS.keys()
        for lang in idiomas_a_revisar:
            if lang in self.cartones:
                for carton in self.cartones[lang].values():
                    resultado.append({
                        "id": carton.id,
                        "idioma": IDIOMAS[lang]["nombre"],
                        "progreso": f"{carton.aciertos}/{len(carton.palabras)}",
                        "es_ganador": carton.es_ganador
                    })
        return resultado
