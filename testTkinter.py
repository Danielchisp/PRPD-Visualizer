import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser


class AplicacionTkinter:
    def __init__(self, root):
        self.root = root
        self.root.title("Demo Completo de Tkinter")
        self.root.geometry("800x600")

        # Configurar grid principal
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Crear notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Pestaña de Widgets Básicos
        self.crear_pestana_widgets()

        # Pestaña de Diálogos
        self.crear_pestana_dialogos()

        # Pestaña de Menús
        self.crear_pestana_menus()

        # Pestaña de Canvas y Gráficos
        self.crear_pestana_canvas()

        # Pestaña de Treeview
        self.crear_pestana_treeview()

    def crear_pestana_widgets(self):
        """Crear pestaña con widgets básicos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Widgets Básicos")

        # Configurar grid
        for i in range(4):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(8):
            frame.grid_rowconfigure(i, weight=1)

        # Label
        ttk.Label(frame, text="Ejemplo de Label").grid(row=0, column=0, padx=5, pady=5)

        # Entry
        self.entry_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.entry_var).grid(
            row=0, column=1, padx=5, pady=5
        )

        # Button
        ttk.Button(frame, text="Botón", command=self.mostrar_texto_entry).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Checkbutton
        self.check_var = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Checkbutton", variable=self.check_var).grid(
            row=1, column=0, padx=5, pady=5
        )

        # Radiobuttons
        self.radio_var = tk.StringVar(value="Opción 1")
        ttk.Label(frame, text="Radiobuttons:").grid(row=2, column=0, padx=5, pady=5)
        ttk.Radiobutton(
            frame, text="Opción 1", variable=self.radio_var, value="Opción 1"
        ).grid(row=2, column=1, padx=5, pady=5)
        ttk.Radiobutton(
            frame, text="Opción 2", variable=self.radio_var, value="Opción 2"
        ).grid(row=2, column=2, padx=5, pady=5)

        # Combobox
        ttk.Label(frame, text="Combobox:").grid(row=3, column=0, padx=5, pady=5)
        self.combo = ttk.Combobox(frame, values=["Item 1", "Item 2", "Item 3"])
        self.combo.grid(row=3, column=1, padx=5, pady=5)

        # Spinbox
        ttk.Label(frame, text="Spinbox:").grid(row=4, column=0, padx=5, pady=5)
        self.spinbox = ttk.Spinbox(frame, from_=0, to=10)
        self.spinbox.grid(row=4, column=1, padx=5, pady=5)

        # Scale
        ttk.Label(frame, text="Scale:").grid(row=5, column=0, padx=5, pady=5)
        self.scale = ttk.Scale(frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.scale.grid(row=5, column=1, padx=5, pady=5)

        # Progressbar
        ttk.Label(frame, text="Progressbar:").grid(row=6, column=0, padx=5, pady=5)
        self.progress = ttk.Progressbar(
            frame, orient=tk.HORIZONTAL, length=200, mode="determinate"
        )
        self.progress.grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(frame, text="Iniciar", command=self.iniciar_progressbar).grid(
            row=6, column=2, padx=5, pady=5
        )

        # Text widget con Scrollbar
        ttk.Label(frame, text="Text widget:").grid(row=7, column=0, padx=5, pady=5)
        text_frame = ttk.Frame(frame)
        text_frame.grid(row=7, column=1, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.text = tk.Text(text_frame, height=5, width=40)
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=self.text.yview
        )
        self.text.configure(yscrollcommand=scrollbar.set)

        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Insertar texto de ejemplo
        self.text.insert(
            "1.0",
            "Este es un widget Text con barra de desplazamiento.\nPuedes escribir múltiples líneas aquí.",
        )

    def crear_pestana_dialogos(self):
        """Crear pestaña con diálogos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Diálogos")

        # Configurar grid
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)
        for i in range(5):
            frame.grid_rowconfigure(i, weight=1)

        # Messagebox
        ttk.Button(
            frame, text="Mostrar Messagebox", command=self.mostrar_messagebox
        ).grid(row=0, column=0, padx=10, pady=10)

        # Filedialog (abrir archivo)
        ttk.Button(frame, text="Abrir Archivo", command=self.abrir_archivo).grid(
            row=1, column=0, padx=10, pady=10
        )

        # Filedialog (guardar archivo)
        ttk.Button(frame, text="Guardar Archivo", command=self.guardar_archivo).grid(
            row=2, column=0, padx=10, pady=10
        )

        # Colorchooser
        ttk.Button(
            frame, text="Seleccionar Color", command=self.seleccionar_color
        ).grid(row=3, column=0, padx=10, pady=10)

        # Frame para mostrar resultados
        self.resultados_frame = ttk.LabelFrame(frame, text="Resultados")
        self.resultados_frame.grid(
            row=0, column=1, rowspan=4, padx=10, pady=10, sticky="nsew"
        )

        self.resultados_label = ttk.Label(
            self.resultados_frame,
            text="Los resultados de los diálogos aparecerán aquí.",
        )
        self.resultados_label.pack(padx=10, pady=10)

    def crear_pestana_menus(self):
        """Crear pestaña con menús"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Menús")

        # Configurar grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Crear menú en la ventana principal (no en el frame)
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(
            label="Nuevo", command=lambda: self.mostrar_accion("Nuevo")
        )
        menu_archivo.add_command(
            label="Abrir", command=lambda: self.mostrar_accion("Abrir")
        )
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)

        # Menú Edición
        menu_edicion = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edición", menu=menu_edicion)
        menu_edicion.add_command(
            label="Copiar", command=lambda: self.mostrar_accion("Copiar")
        )
        menu_edicion.add_command(
            label="Pegar", command=lambda: self.mostrar_accion("Pegar")
        )

        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Acerca de", command=self.mostrar_acerca_de)

        # Mostrar información
        label = ttk.Label(
            frame,
            text="Los menús aparecen en la parte superior de la ventana.\nPrueba a usar los menús 'Archivo', 'Edición' y 'Ayuda'.",
        )
        label.pack(pady=50)

    def crear_pestana_canvas(self):
        """Crear pestaña con Canvas y gráficos"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Canvas")

        # Configurar grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        # Crear Canvas
        self.canvas = tk.Canvas(frame, bg="white", width=600, height=400)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)

        # Dibujar formas
        self.canvas.create_rectangle(50, 50, 150, 150, fill="blue", outline="black")
        self.canvas.create_oval(200, 50, 300, 150, fill="red", outline="black")
        self.canvas.create_line(350, 50, 450, 150, width=3, fill="green")
        self.canvas.create_polygon(500, 50, 550, 150, 450, 150, fill="purple")

        # Dibujar texto
        self.canvas.create_text(
            300, 200, text="¡Esto es un Canvas!", font=("Arial", 16, "bold")
        )

        # Dibujar imagen (si está disponible)
        try:
            self.image = tk.PhotoImage(file="python_logo.png")
            self.canvas.create_image(100, 250, image=self.image, anchor="nw")
        except:
            self.canvas.create_text(100, 250, text="Imagen no encontrada", anchor="nw")

    def crear_pestana_treeview(self):
        """Crear pestaña con Treeview (tabla)"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Treeview")

        # Configurar grid
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)

        # Crear Treeview con Scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.tree = ttk.Treeview(
            tree_frame, columns=("Nombre", "Edad", "Ciudad"), show="headings"
        )

        # Configurar columnas
        self.tree.heading("Nombre", text="Nombre")
        self.tree.heading("Edad", text="Edad")
        self.tree.heading("Ciudad", text="Ciudad")

        self.tree.column("Nombre", width=200)
        self.tree.column("Edad", width=100, anchor="center")
        self.tree.column("Ciudad", width=200)

        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Insertar datos de ejemplo
        datos = [
            ("Juan Pérez", 30, "Madrid"),
            ("María García", 25, "Barcelona"),
            ("Carlos López", 35, "Valencia"),
            ("Ana Martínez", 28, "Sevilla"),
            ("Pedro Sánchez", 40, "Bilbao"),
        ]

        for dato in datos:
            self.tree.insert("", "end", values=dato)

        # Botones para interactuar con el Treeview
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        ttk.Button(btn_frame, text="Añadir Fila", command=self.anadir_fila).pack(
            side="left", padx=5
        )
        ttk.Button(btn_frame, text="Eliminar Fila", command=self.eliminar_fila).pack(
            side="left", padx=5
        )
        ttk.Button(
            btn_frame, text="Obtener Selección", command=self.obtener_seleccion
        ).pack(side="left", padx=5)

    # Métodos para funcionalidad de los widgets

    def mostrar_texto_entry(self):
        """Mostrar el texto del Entry en un messagebox"""
        texto = self.entry_var.get()
        messagebox.showinfo("Texto del Entry", f"Has escrito: {texto}")

    def iniciar_progressbar(self):
        """Iniciar la progressbar"""
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.actualizar_progressbar()

    def actualizar_progressbar(self):
        """Actualizar el valor de la progressbar"""
        if self.progress["value"] < 100:
            self.progress["value"] += 10
            self.root.after(500, self.actualizar_progressbar)

    def mostrar_messagebox(self):
        """Mostrar diferentes tipos de messagebox"""
        respuesta = messagebox.askyesno(
            "Pregunta", "¿Quieres ver un mensaje de información?"
        )
        if respuesta:
            messagebox.showinfo("Información", "Este es un mensaje de información")
            messagebox.showwarning("Advertencia", "Este es un mensaje de advertencia")
            messagebox.showerror("Error", "Este es un mensaje de error")

    def abrir_archivo(self):
        """Mostrar diálogo para abrir archivo"""
        archivo = filedialog.askopenfilename(
            title="Abrir archivo",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")),
        )
        if archivo:
            self.resultados_label.config(text=f"Archivo seleccionado:\n{archivo}")

    def guardar_archivo(self):
        """Mostrar diálogo para guardar archivo"""
        archivo = filedialog.asksaveasfilename(
            title="Guardar archivo",
            defaultextension=".txt",
            filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")),
        )
        if archivo:
            self.resultados_label.config(text=f"Archivo a guardar:\n{archivo}")

    def seleccionar_color(self):
        """Mostrar diálogo para seleccionar color"""
        color = colorchooser.askcolor(title="Elige un color")
        if color[1]:  # color[1] es el código hexadecimal
            self.resultados_label.config(
                text=f"Color seleccionado:\n{color[1]}", background=color[1]
            )

    def mostrar_accion(self, accion):
        """Mostrar la acción seleccionada en el menú"""
        messagebox.showinfo("Acción del menú", f"Has seleccionado: {accion}")

    def mostrar_acerca_de(self):
        """Mostrar información 'Acerca de'"""
        messagebox.showinfo(
            "Acerca de",
            "Demo de Tkinter\n\nMuestra las principales funcionalidades de Tkinter",
        )

    def anadir_fila(self):
        """Añadir una fila al Treeview"""
        self.tree.insert("", "end", values=("Nueva persona", 0, "Desconocida"))

    def eliminar_fila(self):
        """Eliminar la fila seleccionada del Treeview"""
        seleccion = self.tree.selection()
        if seleccion:
            self.tree.delete(seleccion)

    def obtener_seleccion(self):
        """Obtener la fila seleccionada del Treeview"""
        seleccion = self.tree.selection()
        if seleccion:
            valores = self.tree.item(seleccion, "values")
            messagebox.showinfo("Fila seleccionada", f"Valores:\n{valores}")
        else:
            messagebox.showwarning("Advertencia", "No hay ninguna fila seleccionada")


# Crear y ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionTkinter(root)
    root.mainloop()
