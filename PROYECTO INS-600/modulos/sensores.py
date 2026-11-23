import customtkinter as ctk
from tkinter import ttk, messagebox

class Sensores(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Título
        ctk.CTkLabel(self, text="Gestión de Nodos Sensores", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Administre los dispositivos instalados en la ladera de riesgo.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 20))

        # --- PANEL DE REGISTRO ---
        frame_form = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_form.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_form, text="Registrar Nuevo Nodo:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.entry_codigo = ctk.CTkEntry(frame_form, placeholder_text="Código (Ej. Nodo 6)", width=150)
        self.entry_codigo.grid(row=0, column=1, padx=10, pady=20)
        
        self.entry_ubicacion = ctk.CTkEntry(frame_form, placeholder_text="Ubicación (Ej. Ladera Este)", width=250)
        self.entry_ubicacion.grid(row=0, column=2, padx=10, pady=20)
        
        ctk.CTkButton(frame_form, text="Agregar Sensor", fg_color="#1f538d", command=self.agregar).grid(row=0, column=3, padx=20, pady=20)

        # --- TABLA DE SENSORES ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="#00BFFF", font=("Arial", 12, "bold"))
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tabla = ttk.Treeview(self, columns=("ID", "Codigo", "Ubicacion", "Estado", "Accion"), show="headings")
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Codigo", text="Código")
        self.tabla.heading("Ubicacion", text="Ubicación")
        self.tabla.heading("Estado", text="Estado")
        self.tabla.heading("Accion", text="Prueba Manual")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Codigo", width=100, anchor="center")
        self.tabla.column("Ubicacion", width=250)
        self.tabla.column("Estado", width=100, anchor="center")
        self.tabla.column("Accion", width=150, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=5, pady=10)

        # Botón para simular prueba de sirena (RF-08)
        ctk.CTkButton(self, text="🔊 Probar Sirena del Nodo Seleccionado", fg_color="#FFD700", text_color="black", command=self.probar_sirena).pack(pady=10)

        self.cargar()

    def cargar(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, codigo, ubicacion, estado FROM sensores")
            for fila in cursor.fetchall():
                self.tabla.insert("", "end", values=(fila[0], fila[1], fila[2], fila[3], "Hacer Clic aquí"))
            conn.close()

    def agregar(self):
        cod = self.entry_codigo.get()
        ubi = self.entry_ubicacion.get()
        if cod and ubi:
            try:
                conn = self.db.conectar()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO sensores (codigo, ubicacion) VALUES (%s, %s)", (cod, ubi))
                conn.commit()
                conn.close()
                self.entry_codigo.delete(0, 'end')
                self.entry_ubicacion.delete(0, 'end')
                self.cargar()
                messagebox.showinfo("Éxito", "Nodo sensor registrado correctamente.")
            except:
                messagebox.showerror("Error", "No se pudo registrar el sensor.")

    def probar_sirena(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Seleccione un nodo de la tabla para probar su sirena.")
            return
        
        item = self.tabla.item(seleccion[0])
        codigo_nodo = item['values'][1]
        
        # Simulación de la prueba manual de hardware
        messagebox.showinfo("Prueba Manual (RF-08)", f"Enviando comando de prueba al {codigo_nodo}...\n\n🔊 SIRENA ACTIVADA POR 3 SEGUNDOS.\n💡 LUCES LED PARPADEANDO.\n\nPrueba exitosa.")