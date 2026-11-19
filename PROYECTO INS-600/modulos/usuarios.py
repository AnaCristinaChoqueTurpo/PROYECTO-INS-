import customtkinter as ctk
from tkinter import ttk, messagebox

class Usuarios(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Título
        ctk.CTkLabel(self, text="Gestión de Usuarios del Sistema", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Administre los accesos del personal técnico y administradores.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 20))

        # --- PANEL DE REGISTRO ---
        frame_form = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_form.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_form, text="Registrar Nuevo Usuario:", font=("Arial", 14, "bold")).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        self.entry_nombre = ctk.CTkEntry(frame_form, placeholder_text="Nombre completo", width=150)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=20)
        
        self.entry_user = ctk.CTkEntry(frame_form, placeholder_text="Usuario", width=120)
        self.entry_user.grid(row=0, column=2, padx=5, pady=20)
        
        self.entry_pass = ctk.CTkEntry(frame_form, placeholder_text="Contraseña", show="*", width=120)
        self.entry_pass.grid(row=0, column=3, padx=5, pady=20)

        self.combo_rol = ctk.CTkComboBox(frame_form, values=["Técnico", "Administrador"], width=120)
        self.combo_rol.grid(row=0, column=4, padx=5, pady=20)
        
        ctk.CTkButton(frame_form, text="Crear Usuario", fg_color="#1f538d", command=self.crear).grid(row=0, column=5, padx=20, pady=20)

        # --- TABLA DE USUARIOS ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="#00BFFF", font=("Arial", 12, "bold"))
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tabla = ttk.Treeview(self, columns=("ID", "Nombre", "Usuario", "Rol"), show="headings")
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre Completo")
        self.tabla.heading("Usuario", text="Usuario de Acceso")
        self.tabla.heading("Rol", text="Rol en el Sistema")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Nombre", width=250, anchor="w")
        self.tabla.column("Usuario", width=150, anchor="center")
        self.tabla.column("Rol", width=150, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=5, pady=10)

        self.cargar()

    def cargar(self):
        for item in self.tabla.get_children(): self.tabla.delete(item)
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios")
            for fila in cursor.fetchall():
                self.tabla.insert("", "end", values=fila)
            conn.close()

    def crear(self):
        nombre = self.entry_nombre.get()
        user = self.entry_user.get()
        password = self.entry_pass.get()
        rol = self.combo_rol.get()

        if not nombre or not user or not password:
            messagebox.showwarning("Aviso", "Todos los campos son obligatorios.")
            return

        try:
            conn = self.db.conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, usuario, password, rol) VALUES (%s, %s, %s, %s)", 
                           (nombre, user, password, rol))
            conn.commit()
            conn.close()
            
            # Limpiar campos
            self.entry_nombre.delete(0, 'end')
            self.entry_user.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            
            self.cargar()
            messagebox.showinfo("Éxito", f"Usuario '{user}' registrado correctamente como {rol}.")
        except Exception as e:
            messagebox.showerror("Error", "El nombre de usuario ya existe. Intente con otro.")