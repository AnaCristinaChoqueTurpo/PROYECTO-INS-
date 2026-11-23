import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class Login(ctk.CTkToplevel):
    def __init__(self, app, db):
        super().__init__()
        self.app = app
        self.db = db
        
        self.title("Acceso al Sistema - Alerta Temprana")
        self.geometry("400x550") 
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.app.destroy)

        # --- LOGO INSTITUCIONAL ---
        try:
            img = Image.open("logo.png")
            img_logo = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
            self.lbl_logo = ctk.CTkLabel(self, text="", image=img_logo)
            self.lbl_logo.pack(pady=(20, 0))
        except Exception as e:
            ctk.CTkLabel(self, text="⚠️ Logo no encontrado", font=("Arial", 12), text_color="red").pack(pady=(20, 0))
            print(f"Error cargando logo: {e}")

        # Diseño del Login
        ctk.CTkLabel(self, text="SISTEMA DE ALERTA TEMPRANA", font=("Arial", 18, "bold"), text_color="#00BFFF").pack(pady=(10, 0))
        ctk.CTkLabel(self, text="Monitoreo de Deslizamientos ", font=("Arial", 11), text_color="gray").pack(pady=(0, 30))
        
        # Campos
        self.user = ctk.CTkEntry(self, placeholder_text="👤 Ingrese su usuario", width=300, height=40)
        self.user.pack(pady=10)
        
        # --- CC-03: Frame para la contraseña y el ojito ---
        frame_pass = ctk.CTkFrame(self, fg_color="transparent")
        frame_pass.pack(pady=10)
        
        self.password = ctk.CTkEntry(frame_pass, placeholder_text="🔒 Contraseña", show="*", width=240, height=40)
        self.password.pack(side="left", padx=(0, 10))
        
        # Botón del ojito
        self.btn_ver = ctk.CTkButton(frame_pass, text="👁️", width=40, height=40, fg_color="#333333", hover_color="#555555", command=self.toggle_password)
        self.btn_ver.pack(side="left")
        
        # Botón Ingresar
        ctk.CTkButton(self, text="INGRESAR AL SISTEMA", width=300, height=40, fg_color="#1f538d", font=("Arial", 13, "bold"), command=self.validar).pack(pady=30)

        # Footer
        ctk.CTkLabel(self, text="Escuela Industrial Superior Pedro Domingo Murillo", font=("Arial", 9), text_color="gray").pack(side="bottom", pady=10)

    # --- Función para mostrar/ocultar (CC-03) ---
    def toggle_password(self):
        if self.password.cget("show") == "*":
            self.password.configure(show="")
            self.btn_ver.configure(text="🙈") # Cambia a un monito
        else:
            self.password.configure(show="*")
            self.btn_ver.configure(text="👁️") # Vuelve al ojito

    def validar(self):
        u = self.user.get()
        p = self.password.get()

        if not u or not p:
            messagebox.showwarning("Aviso", "Por favor, llene todos los campos.")
            return

        if self.db.validar_usuario(u, p):
            self.destroy()
            self.app.deiconify() 
            self.app.crear_interfaz() 
        else:
            messagebox.showerror("Error de Acceso", "Usuario o contraseña incorrectos.\nVerifique sus credenciales.")