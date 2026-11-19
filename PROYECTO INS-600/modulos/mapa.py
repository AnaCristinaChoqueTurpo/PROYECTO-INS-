import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class Mapa(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Título
        ctk.CTkLabel(self, text="Mapa de Monitoreo Geoespacial", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Distribución de los 5 nodos sensores en la ladera de riesgo.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 20))

        # Panel principal del Mapa
        self.frame_mapa = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        self.frame_mapa.pack(fill="both", expand=True, padx=10, pady=10)

        # Lienzo (Canvas) para dibujar el mapa
        self.canvas = tk.Canvas(self.frame_mapa, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Botón de actualizar
        ctk.CTkButton(self, text="🔄 Actualizar Estado de los Nodos", command=self.dibujar_mapa).pack(pady=10)
        
        # Diccionario para guardar el estado de los nodos
        self.estados_nodos = {}

        self.dibujar_mapa()

    def dibujar_mapa(self):
        self.canvas.delete("all")
        
        # 1. Dibujar el contorno de la ladera (simulada)
        self.canvas.create_polygon(50, 450, 250, 150, 500, 250, 750, 100, 950, 400, fill="#1a2e1a", outline="#4CAF50", width=3)
        self.canvas.create_text(500, 480, text="LADERA DE RIESGO - ALTIPLANO BOLIVIANO", fill="white", font=("Arial", 14, "bold"))

        # 2. Obtener últimos estados de la base de datos para simular el color de cada nodo
        conn = self.db.conectar()
        nivel_actual = "VERDE"
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nivel_alerta FROM registros ORDER BY id DESC LIMIT 1")
            res = cursor.fetchone()
            if res: nivel_actual = res[0]
            conn.close()

        # 3. Coordenadas de los nodos (X, Y, Nombre)
        nodos = [
            (150, 300, "Nodo 1"),
            (280, 220, "Nodo 2"),
            (450, 260, "Nodo 3"),
            (650, 180, "Nodo 4"),
            (800, 320, "Nodo 5")
        ]

        # 4. Dibujar líneas de comunicación (Topología estrella simulada)
        self.canvas.create_oval(460, 360, 540, 440, fill="#1f538d", outline="white") # Nodo Coordinador
        self.canvas.create_text(500, 400, text="Coordinador", fill="white", font=("Arial", 10, "bold"))

        for x, y, nombre in nodos:
            # Línea hacia el coordinador
            self.canvas.create_line(x, y, 500, 400, fill="#555555", dash=(5, 3))
            
            # Color según estado (Simulación)
            if "PELIGRO" in nivel_actual:
                color_nodo = "#FF0000"
                texto_estado = "Peligro"
            elif "PRECAUCIÓN" in nivel_actual:
                color_nodo = "#FFD700"
                texto_estado = "Precaución"
            else:
                color_nodo = "#00FF00"
                texto_estado = "Normal"

            # Dibujar el Nodo
            self.canvas.create_oval(x-20, y-20, x+20, y+20, fill=color_nodo, outline="white", width=2)
            self.canvas.create_text(x, y-35, text=nombre, fill="white", font=("Arial", 10, "bold"))
            self.canvas.create_text(x, y+35, text=texto_estado, fill=color_nodo, font=("Arial", 9))