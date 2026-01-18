import os

RUTA_REPOSITORIO = os.path.join(os.path.dirname(__file__), "repositorio")

IDIOMAS = {
    "SP": {"nombre": "Español", "max_palabras": 24},
    "EN": {"nombre": "Inglés", "max_palabras": 14},
    "PT": {"nombre": "Portugués", "max_palabras": 20},
    "DT": {"nombre": "Dutch", "max_palabras": 10}
}
