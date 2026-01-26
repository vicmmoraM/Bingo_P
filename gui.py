"""
================================================================================
[Módulo GUI - Interfaz Gráfica de Usuario para Bingo_P]
================================================================================

Autores:
    - Victor Morales
    - Andres Saltos
    - Darwin Diaz
    - Juliana Burgos
    - Gabriel Tumbaco

Curso: Análisis de Algoritmos II PAO 2025 - Paralelo 2 - Grupo 2

Descripción:
    Módulo que define la clase BingoApp, responsable de la interfaz gráfica
    de usuario para el juego Bingo_P.

Referencias:
    - Claude Sonnet 4.5 para el apoyo con la interfaz grafica del sistema
================================================================================
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from bingo_p import GestorBingo, RepositorioPalabras, IDIOMAS, distancia_edicion


class BingoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bingo_P - Bingo con Palabras")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        self.gestor = GestorBingo()
        self.repositorio = RepositorioPalabras()
        self.partida_activa = False
        self.configurar_estilo()
        self.crear_menu()
        self.crear_interfaz()
        self.actualizar_estadisticas()

    def configurar_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 10))
        style.configure('Winner.TLabel', font=('Helvetica', 12, 'bold'), foreground='green')
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))

    def crear_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Cargar cartones...", command=self.cargar_archivo)
        menu_archivo.add_command(label="Nuevo juego", command=self.reiniciar_todo)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

    def crear_interfaz(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tab_cartones = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_cartones, text="📋 Gestión de Cartones")
        self.crear_tab_cartones()
        self.tab_partida = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_partida, text="🎮 Partida")
        self.crear_tab_partida()
        self.tab_stats = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stats, text="📊 Estadísticas")
        self.crear_tab_estadisticas()

    def crear_tab_cartones(self):
        frame_carga = ttk.LabelFrame(self.tab_cartones, text="Cargar Cartones", padding=10)
        frame_carga.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(frame_carga, text="📂 Cargar desde archivo",
                   command=self.cargar_archivo).pack(side=tk.LEFT, padx=5)
        self.lbl_archivo = ttk.Label(frame_carga, text="Ningún archivo cargado")
        self.lbl_archivo.pack(side=tk.LEFT, padx=20)
        frame_manual = ttk.LabelFrame(self.tab_cartones, text="Agregar Cartón Manual", padding=10)
        frame_manual.pack(fill=tk.X, padx=10, pady=5)
        frame_id = ttk.Frame(frame_manual)
        frame_id.pack(fill=tk.X, pady=2)
        ttk.Label(frame_id, text="ID (ej: SP123456):").pack(side=tk.LEFT)
        self.entry_id = ttk.Entry(frame_id, width=15)
        self.entry_id.pack(side=tk.LEFT, padx=5)
        ttk.Label(frame_id, text="Jugador ID (ej: J001):").pack(side=tk.LEFT, padx=(20, 0))
        self.entry_jugador = ttk.Entry(frame_id, width=10)
        self.entry_jugador.pack(side=tk.LEFT, padx=5)
        frame_palabras = ttk.Frame(frame_manual)
        frame_palabras.pack(fill=tk.X, pady=2)
        ttk.Label(frame_palabras, text="Palabras (separadas por espacio):").pack(side=tk.LEFT)
        self.entry_palabras = ttk.Entry(frame_palabras, width=60)
        self.entry_palabras.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame_manual, text="➕ Agregar Cartón",
                   command=self.agregar_carton_manual).pack(pady=5)
        frame_lista = ttk.LabelFrame(self.tab_cartones, text="Cartones Cargados", padding=10)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        frame_filtro = ttk.Frame(frame_lista)
        frame_filtro.pack(fill=tk.X, pady=5)
        ttk.Label(frame_filtro, text="Filtrar por idioma:").pack(side=tk.LEFT)
        self.filtro_idioma = ttk.Combobox(frame_filtro, values=["Todos"] + [IDIOMAS[i]["nombre"] for i in IDIOMAS],
                                          state="readonly", width=15)
        self.filtro_idioma.set("Todos")
        self.filtro_idioma.pack(side=tk.LEFT, padx=5)
        self.filtro_idioma.bind("<<ComboboxSelected>>", lambda e: self.actualizar_lista_cartones())
        columns = ("ID", "Jugador", "Idioma", "Palabras", "Estado")
        self.tree_cartones = ttk.Treeview(frame_lista, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree_cartones.heading(col, text=col)
            if col == "Palabras":
                self.tree_cartones.column(col, width=250)
            elif col == "Jugador":
                self.tree_cartones.column(col, width=80)
            else:
                self.tree_cartones.column(col, width=100)
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree_cartones.yview)
        self.tree_cartones.configure(yscrollcommand=scrollbar.set)
        self.tree_cartones.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def crear_tab_partida(self):
        frame_control = ttk.LabelFrame(self.tab_partida, text="Control de Partida", padding=10)
        frame_control.pack(fill=tk.X, padx=10, pady=5)
        self.btn_iniciar = ttk.Button(frame_control, text="🎲 Iniciar Nueva Partida",
                                       command=self.iniciar_partida, style='Accent.TButton')
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        self.btn_avanzar = ttk.Button(frame_control, text="⏭️ Siguiente Ronda",
                                       command=self.avanzar_ronda, state=tk.DISABLED)
        self.btn_avanzar.pack(side=tk.LEFT, padx=5)
        self.lbl_ronda = ttk.Label(frame_control, text="No hay partida activa", style='Header.TLabel')
        self.lbl_ronda.pack(side=tk.RIGHT, padx=20)
        frame_anunciar = ttk.LabelFrame(self.tab_partida, text="Extraer Palabra", padding=10)
        frame_anunciar.pack(fill=tk.X, padx=10, pady=5)
        self.btn_extraer = ttk.Button(frame_anunciar, text="🎲 Extraer Palabra del Repositorio",
                                       command=self.extraer_palabra, state=tk.DISABLED,
                                       style='Accent.TButton')
        self.btn_extraer.pack(side=tk.LEFT, padx=5)
        self.lbl_restantes = ttk.Label(frame_anunciar, text="", style='Status.TLabel')
        self.lbl_restantes.pack(side=tk.LEFT, padx=10)
        self.lbl_orden = ttk.Label(frame_anunciar, text="", style='Status.TLabel')
        self.lbl_orden.pack(side=tk.RIGHT, padx=10)
        frame_resultados = ttk.Frame(self.tab_partida)
        frame_resultados.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        frame_palabras = ttk.LabelFrame(frame_resultados, text="Palabras Anunciadas", padding=5)
        frame_palabras.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.txt_palabras = scrolledtext.ScrolledText(frame_palabras, width=30, height=15, font=('Courier', 10))
        self.txt_palabras.pack(fill=tk.BOTH, expand=True)
        frame_ganadores = ttk.LabelFrame(frame_resultados, text="🏆 Ganadores", padding=5)
        frame_ganadores.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self.txt_ganadores = scrolledtext.ScrolledText(frame_ganadores, width=30, height=15, font=('Courier', 10), fg='green')
        self.txt_ganadores.pack(fill=tk.BOTH, expand=True)
        frame_estado = ttk.LabelFrame(self.tab_partida, text="Estado de Cartones (Ronda Actual)", padding=5)
        frame_estado.pack(fill=tk.X, padx=10, pady=5)
        columns_estado = ("ID", "Jugador", "Progreso", "Faltan", "Estado")
        self.tree_estado = ttk.Treeview(frame_estado, columns=columns_estado, show="headings", height=5)
        for col in columns_estado:
            self.tree_estado.heading(col, text=col)
            self.tree_estado.column(col, width=100)
        scrollbar_estado = ttk.Scrollbar(frame_estado, orient=tk.VERTICAL, command=self.tree_estado.yview)
        self.tree_estado.configure(yscrollcommand=scrollbar_estado.set)
        self.tree_estado.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_estado.pack(side=tk.RIGHT, fill=tk.Y)

    def crear_tab_estadisticas(self):
        frame_resumen = ttk.LabelFrame(self.tab_stats, text="Resumen General", padding=15)
        frame_resumen.pack(fill=tk.X, padx=10, pady=5)
        self.lbl_total_cartones = ttk.Label(frame_resumen, text="Total de cartones: 0", style='Header.TLabel')
        self.lbl_total_cartones.pack(anchor=tk.W)
        frame_idiomas = ttk.LabelFrame(self.tab_stats, text="Cartones por Idioma", padding=15)
        frame_idiomas.pack(fill=tk.X, padx=10, pady=5)
        self.labels_idiomas = {}
        for idioma, config in IDIOMAS.items():
            frame = ttk.Frame(frame_idiomas)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{config['nombre']}:", width=15).pack(side=tk.LEFT)
            lbl_count = ttk.Label(frame, text="0 cartones")
            lbl_count.pack(side=tk.LEFT, padx=10)
            lbl_max = ttk.Label(frame, text=f"(Máx {config['max_palabras']} palabras/cartón)", style='Status.TLabel')
            lbl_max.pack(side=tk.LEFT)
            progress = ttk.Progressbar(frame, length=200, mode='determinate')
            progress.pack(side=tk.RIGHT, padx=10)
            self.labels_idiomas[idioma] = {"count": lbl_count, "progress": progress}
        frame_partida = ttk.LabelFrame(self.tab_stats, text="Estadísticas de Partida Actual", padding=15)
        frame_partida.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.lbl_estado_partida = ttk.Label(frame_partida, text="No hay partida activa", style='Header.TLabel')
        self.lbl_estado_partida.pack(anchor=tk.W)
        self.lbl_orden_rondas = ttk.Label(frame_partida, text="", style='Status.TLabel')
        self.lbl_orden_rondas.pack(anchor=tk.W, pady=(5, 10))
        self.labels_partida = {}
        for idioma, config in IDIOMAS.items():
            frame = ttk.Frame(frame_partida)
            frame.pack(fill=tk.X, pady=3)
            ttk.Label(frame, text=f"{config['nombre']}:", width=15).pack(side=tk.LEFT)
            lbl_palabras = ttk.Label(frame, text="0 palabras anunciadas", width=20)
            lbl_palabras.pack(side=tk.LEFT, padx=10)
            lbl_ganadores = ttk.Label(frame, text="0 ganadores", width=15)
            lbl_ganadores.pack(side=tk.LEFT, padx=10)
            self.labels_partida[idioma] = {"palabras": lbl_palabras, "ganadores": lbl_ganadores}
        ttk.Button(self.tab_stats, text="🔄 Actualizar Estadísticas",
                   command=self.actualizar_estadisticas).pack(pady=10)

    def cargar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de cartones",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if archivo:
            cargados, fallidos, errores = self.gestor.cargar_desde_archivo(archivo)
            mensaje = f"Cartones cargados: {cargados}\nCartones con error: {fallidos}"
            if errores:
                mensaje += f"\n\nErrores:\n" + "\n".join(errores[:5])
                if len(errores) > 5:
                    mensaje += f"\n... y {len(errores) - 5} errores más."
            if cargados > 0:
                messagebox.showinfo("Carga completada", mensaje)
                self.lbl_archivo.config(text=f"Archivo: {archivo.split('/')[-1]}")
            else:
                messagebox.showwarning("Carga fallida", mensaje)
            self.actualizar_lista_cartones()
            self.actualizar_estadisticas()

    def agregar_carton_manual(self):
        id_carton = self.entry_id.get().strip()
        jugador_id = self.entry_jugador.get().strip() or "N/A"
        palabras = self.entry_palabras.get().strip().split()
        if not id_carton:
            messagebox.showwarning("Error", "Ingrese el ID del cartón")
            return
        if not palabras:
            messagebox.showwarning("Error", "Ingrese al menos una palabra")
            return
        exito, mensaje = self.gestor.agregar_carton(id_carton, palabras, jugador_id)
        if exito:
            messagebox.showinfo("Éxito", mensaje)
            self.entry_id.delete(0, tk.END)
            self.entry_jugador.delete(0, tk.END)
            self.entry_palabras.delete(0, tk.END)
            self.actualizar_lista_cartones()
            self.actualizar_estadisticas()
        else:
            messagebox.showerror("Error", mensaje)

    def actualizar_lista_cartones(self):
        for item in self.tree_cartones.get_children():
            self.tree_cartones.delete(item)
        filtro = self.filtro_idioma.get()
        for idioma, cartones in self.gestor.cartones.items():
            if filtro != "Todos" and IDIOMAS[idioma]["nombre"] != filtro:
                continue
            for id_carton, carton in cartones.items():
                palabras_str = ", ".join(list(carton.palabras)[:5])
                if len(carton.palabras) > 5:
                    palabras_str += f"... (+{len(carton.palabras) - 5})"
                estado = "✓ Ganador" if carton.es_ganador else f"{carton.aciertos}/{len(carton.palabras)}"
                self.tree_cartones.insert("", tk.END, values=(id_carton, carton.jugador_id, IDIOMAS[idioma]["nombre"], palabras_str, estado))

    def actualizar_estadisticas(self):
        stats = self.gestor.obtener_estadisticas()
        self.lbl_total_cartones.config(text=f"Total de cartones: {stats['total_cartones']}")
        max_cartones = max((len(self.gestor.cartones[i]) for i in IDIOMAS), default=1) or 1
        for idioma, labels in self.labels_idiomas.items():
            count = len(self.gestor.cartones[idioma])
            labels["count"].config(text=f"{count} cartones")
            labels["progress"]["value"] = (count / max_cartones) * 100 if max_cartones > 0 else 0
        if self.partida_activa:
            ronda_actual = stats["ronda_actual"]
            self.lbl_estado_partida.config(text=f"Ronda actual: {ronda_actual} de {len(IDIOMAS)}")
            orden_str = " → ".join(stats["orden_rondas"])
            self.lbl_orden_rondas.config(text=f"Orden: {orden_str}")
        else:
            self.lbl_estado_partida.config(text="No hay partida activa")
            self.lbl_orden_rondas.config(text="")
        for idioma, labels in self.labels_partida.items():
            idioma_nombre = IDIOMAS[idioma]["nombre"]
            if idioma_nombre in stats["por_idioma"]:
                palabras = stats["por_idioma"][idioma_nombre]["palabras_anunciadas"]
                ganadores = stats["por_idioma"][idioma_nombre]["ganadores"]
                labels["palabras"].config(text=f"{palabras} palabras anunciadas")
                labels["ganadores"].config(text=f"{ganadores} ganadores")
            else:
                labels["palabras"].config(text="0 palabras anunciadas")
                labels["ganadores"].config(text="0 ganadores")

    def iniciar_partida(self):
        total = sum(len(c) for c in self.gestor.cartones.values())
        if total == 0:
            messagebox.showwarning("Error", "No hay cartones cargados. Cargue cartones primero.")
            return
        orden = self.gestor.iniciar_partida()
        self.partida_activa = True
        self.txt_palabras.delete(1.0, tk.END)
        self.txt_ganadores.delete(1.0, tk.END)
        orden_str = " → ".join(IDIOMAS[i]["nombre"] for i in orden)
        self.lbl_orden.config(text=f"Orden: {orden_str}")
        idioma_actual = self.gestor.obtener_idioma_actual()
        self.lbl_ronda.config(text=f"Ronda: {IDIOMAS[idioma_actual]['nombre']}")
        self.repositorio.reiniciar_ronda()
        self.btn_avanzar.config(state=tk.NORMAL)
        self.btn_extraer.config(state=tk.NORMAL)
        self.actualizar_estado_ronda()
        self.actualizar_palabras_restantes()
        self.actualizar_lista_cartones()
        self.actualizar_estadisticas()
        messagebox.showinfo("Partida Iniciada",
                           f"¡Nueva partida iniciada!\n\nOrden de rondas:\n{orden_str}\n\n"
                           f"Comienza la ronda de {IDIOMAS[idioma_actual]['nombre']}")

    def extraer_palabra(self):
        if not self.partida_activa:
            return
        idioma_actual = self.gestor.obtener_idioma_actual()
        if idioma_actual is None:
            return
        if self.gestor.ganadores.get(idioma_actual, []):
            messagebox.showinfo("Ronda finalizada",
                               f"Ya hay un ganador en la ronda de {IDIOMAS[idioma_actual]['nombre']}.\n"
                               "Avanza a la siguiente ronda para continuar.")
            return
        if self.gestor.limite_alcanzado():
            messagebox.showwarning("Límite alcanzado",
                                   f"Se alcanzó el límite de extracciones para {IDIOMAS[idioma_actual]['nombre']}.\n"
                                   "Avanza a la siguiente ronda para continuar.")
            return
        palabra = self.repositorio.extraer_palabra(idioma_actual)
        if palabra is None:
            messagebox.showwarning("Repositorio agotado",
                                   f"No quedan más palabras en el repositorio de {IDIOMAS[idioma_actual]['nombre']}")
            return
        ganadores = self.gestor.anunciar_palabra(palabra)
        self.txt_palabras.insert(tk.END, f"• {palabra}\n")
        self.txt_palabras.see(tk.END)
        if ganadores:
            for carton in ganadores:
                self.txt_ganadores.insert(tk.END, f"🏆 {carton.id}\n")
                self.txt_ganadores.insert(tk.END, f"   Jugador: {carton.jugador_id}\n")
                self.txt_ganadores.insert(tk.END, f"   ({IDIOMAS[idioma_actual]['nombre']})\n\n")
            self.txt_ganadores.see(tk.END)
            self.btn_extraer.config(state=tk.DISABLED)
            messagebox.showinfo("¡GANADOR!",
                               f"¡Cartón(es) ganador(es)!\n\n" +
                               "\n".join(f"• {c.id} - Jugador: {c.jugador_id}" for c in ganadores) +
                               "\n\nLa ronda ha finalizado. Avanza a la siguiente ronda.")
        elif self.gestor.limite_alcanzado():
            self.btn_extraer.config(state=tk.DISABLED)
            extracciones, limite = self.gestor.obtener_extracciones_info()
            self.txt_ganadores.insert(tk.END, f"❌ Sin ganador\n")
            self.txt_ganadores.insert(tk.END, f"   ({IDIOMAS[idioma_actual]['nombre']})\n\n")
            self.txt_ganadores.see(tk.END)
            messagebox.showinfo("Ronda sin ganador",
                               f"Se alcanzó el límite de {limite} extracciones.\n\n"
                               f"No hubo ganador en la ronda de {IDIOMAS[idioma_actual]['nombre']}.\n\n"
                               "Avanza a la siguiente ronda para continuar.")
        self.actualizar_estado_ronda()
        self.actualizar_palabras_restantes()
        self.actualizar_estadisticas()

    def actualizar_palabras_restantes(self):
        idioma_actual = self.gestor.obtener_idioma_actual()
        if idioma_actual is None:
            self.lbl_restantes.config(text="")
            return
        extracciones, limite = self.gestor.obtener_extracciones_info()
        self.lbl_restantes.config(text=f"Extracciones: {extracciones}/{limite}")

    def avanzar_ronda(self):
        if not self.partida_activa:
            return
        idioma_anterior = self.gestor.obtener_idioma_actual()
        ganadores_ronda = self.gestor.ganadores.get(idioma_anterior, [])
        if ganadores_ronda:
            resumen = f"Ganadores de {IDIOMAS[idioma_anterior]['nombre']}:\n" + \
                      "\n".join(f"• {g}" for g in ganadores_ronda)
        else:
            resumen = f"No hubo ganadores en la ronda de {IDIOMAS[idioma_anterior]['nombre']}"
        hay_mas, mensaje = self.gestor.avanzar_ronda()
        if hay_mas:
            idioma_actual = self.gestor.obtener_idioma_actual()
            self.lbl_ronda.config(text=f"Ronda: {IDIOMAS[idioma_actual]['nombre']}")
            self.txt_palabras.insert(tk.END, f"\n--- {IDIOMAS[idioma_actual]['nombre']} ---\n")
            self.btn_extraer.config(state=tk.NORMAL)
            self.actualizar_estado_ronda()
            self.actualizar_palabras_restantes()
            self.actualizar_estadisticas()
            messagebox.showinfo("Nueva Ronda", f"{resumen}\n\n{mensaje}")
        else:
            self.partida_activa = False
            self.btn_avanzar.config(state=tk.DISABLED)
            self.btn_extraer.config(state=tk.DISABLED)
            self.lbl_ronda.config(text="Partida Finalizada")
            self.lbl_restantes.config(text="")
            self.actualizar_estadisticas()
            messagebox.showinfo("Partida Finalizada", f"{resumen}\n\n¡Todas las rondas han terminado!")

    def actualizar_estado_ronda(self):
        for item in self.tree_estado.get_children():
            self.tree_estado.delete(item)
        idioma_actual = self.gestor.obtener_idioma_actual()
        if idioma_actual is None:
            return
        cartones = self.gestor.cartones[idioma_actual]
        for id_carton, carton in cartones.items():
            faltan = len(carton.palabras) - carton.aciertos
            estado = "✓ GANADOR" if carton.es_ganador else "En juego"
            self.tree_estado.insert("", tk.END, values=(id_carton, carton.jugador_id, f"{carton.aciertos}/{len(carton.palabras)}", faltan, estado))

    def reiniciar_todo(self):
        if messagebox.askyesno("Confirmar", "¿Desea reiniciar todo? Se perderán todos los cartones cargados."):
            self.gestor = GestorBingo()
            self.partida_activa = False
            self.txt_palabras.delete(1.0, tk.END)
            self.txt_ganadores.delete(1.0, tk.END)
            self.lbl_archivo.config(text="Ningún archivo cargado")
            self.lbl_ronda.config(text="No hay partida activa")
            self.lbl_orden.config(text="")
            self.btn_avanzar.config(state=tk.DISABLED)
            self.btn_extraer.config(state=tk.DISABLED)
            self.lbl_restantes.config(text="")
            self.actualizar_lista_cartones()
            self.actualizar_estadisticas()

    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de Bingo_P",
                           "Bingo_P - Bingo con Palabras\n\n"
                           "Proyecto Final - Análisis de Algoritmos\n\n"
                           "Estrategia: Híbrida\n"
                           "• Particionamiento por idioma\n"
                           "• Índice invertido para búsqueda O(1)\n"
                           "• Contadores incrementales\n\n"
                           "Grupo 2")


def main():
    root = tk.Tk()
    app = BingoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()