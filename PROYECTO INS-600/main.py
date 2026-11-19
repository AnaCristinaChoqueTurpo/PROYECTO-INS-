import customtkinter as ctk
from database import BaseDatos
from modulos.login import Login
from modulos.inicio import Inicio
from modulos.monitoreo import Monitoreo
from modulos.simulacion import Simulacion # <-- Nueva importación
from modulos.mapa import Mapa
from modulos.sensores import Sensores
from modulos.historial import Historial
from modulos.usuarios import Usuarios

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Alerta Temprana - Altiplano Boliviano")
        self.geometry("1150x700")
        self.withdraw()
        
        self.db = BaseDatos()
        Login(self, self.db)

    def crear_interfaz(self):
        # --- MENÚ LATERAL ---
        self.sidebar = ctk.CTkFrame(self, width=230, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="⛰️ ALERTA TEMPRANA", font=("Arial", 18, "bold"), text_color="#00BFFF").pack(pady=(30, 10))
        ctk.CTkLabel(self.sidebar, text="Sistema de Monitoreo v1.0", font=("Arial", 11), text_color="gray").pack(pady=(0, 30))

        self.botones = {}
        opciones = [
            ("🏠 Inicio", "inicio"),
            ("📊 Monitoreo", "monitoreo"),
            ("🚨 Simulador de Desastre", "simulacion"), # <-- Botón de Simulación
            ("🗺️ Mapa de Nodos", "mapa"),
            ("📡 Sensores", "sensores"),
            ("📋 Historial", "historial"),
            ("👥 Usuarios", "usuarios")
        ]

        for texto, vista in opciones:
            btn = ctk.CTkButton(self.sidebar, text=texto, anchor="w", fg_color="transparent", 
                                text_color="white", hover_color="#333333", font=("Arial", 14),
                                command=lambda v=vista: self.mostrar(v))
            btn.pack(pady=5, padx=10, fill="x")
            self.botones[vista] = btn

        ctk.CTkButton(self.sidebar, text="🚪 Cerrar Sesión", fg_color="#8B0000", hover_color="#5c0000", 
                      command=self.destroy).pack(pady=20, padx=10, fill="x", side="bottom")
        
        ctk.CTkLabel(self.sidebar, text="Admin", text_color="gray").pack(side="bottom", pady=10)

        # --- CONTENEDOR PRINCIPAL ---
        self.container = ctk.CTkFrame(self, fg_color="#121212", corner_radius=0)
        self.container.pack(side="right", fill="both", expand=True)

        # Instanciar TODAS las pantallas
        self.vistas = {
            "inicio": Inicio(self.container, self.db),
            "monitoreo": Monitoreo(self.container, self.db),
            "simulacion": Simulacion(self.container, self.db),
            "mapa": Mapa(self.container, self.db),
            "sensores": Sensores(self.container, self.db),
            "historial": Historial(self.container, self.db),
            "usuarios": Usuarios(self.container, self.db)
        }

        self.mostrar("inicio")

    def mostrar(self, nombre):
        for vista in self.vistas.values():
            vista.pack_forget()
        for btn in self.botones.values():
            btn.configure(fg_color="transparent")

        self.vistas[nombre].pack(fill="both", expand=True, padx=30, pady=30)
        self.botones[nombre].configure(fg_color="#1f538d")

if __name__ == "__main__":
    app = App()
    app.mainloop()