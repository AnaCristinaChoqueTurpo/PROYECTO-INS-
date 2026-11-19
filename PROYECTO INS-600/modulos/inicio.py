import customtkinter as ctk

class Inicio(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Título
        ctk.CTkLabel(self, text="Panel de Control General", font=("Arial", 28, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Resumen del estado actual del sistema de monitoreo.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 30))

        # --- TARJETAS DE ESTADÍSTICAS ---
        frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        frame_cards.pack(fill="x", pady=10)

        self.crear_tarjeta(frame_cards, "Nodos Sensores", "Consultando...", "#00BFFF")
        self.crear_tarjeta(frame_cards, "Total Alertas Registradas", "Consultando...", "#FFD700")
        self.crear_tarjeta(frame_cards, "Estado Base de Datos", "Conectado", "#00FF00")
        
        # --- PANEL DE ESTADO DEL SISTEMA ---
        frame_estado = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=15)
        frame_estado.pack(fill="x", pady=30, ipady=20)

        ctk.CTkLabel(frame_estado, text="Estado Operativo del Sistema", font=("Arial", 18, "bold")).pack(pady=10)
        ctk.CTkLabel(frame_estado, text="🟢 El sistema se encuentra operativo. Los nodos están enviando datos por LoRa correctamente.", font=("Arial", 16), text_color="#00FF00").pack(pady=10)
        
        # Información de la versión
        ctk.CTkLabel(self, text="Versión del Software: v1.0 | Desarrollado por: Ana Cristina Choque Turpo", text_color="gray").pack(side="bottom", pady=10)

        # Actualizar los datos al cargar
        self.actualizar_estadisticas()

    def crear_tarjeta(self, master, titulo, valor_inicial, color):
        card = ctk.CTkFrame(master, fg_color="#2b2b2b", corner_radius=15, height=120)
        card.pack(side="left", padx=10, fill="x", expand=True)
        card.pack_propagate(False)
        
        ctk.CTkLabel(card, text=titulo, font=("Arial", 14), text_color="gray").pack(pady=(20, 10))
        lbl_valor = ctk.CTkLabel(card, text=valor_inicial, font=("Arial", 28, "bold"), text_color=color)
        lbl_valor.pack()
        
        # Guardamos la referencia para actualizar el valor luego
        if "Nodos" in titulo:
            self.lbl_nodos = lbl_valor
        elif "Alertas" in titulo:
            self.lbl_alertas = lbl_valor

    def actualizar_estadisticas(self):
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            
            # Contar sensores
            cursor.execute("SELECT COUNT(*) FROM sensores")
            total_sensores = cursor.fetchone()[0]
            self.lbl_nodos.configure(text=str(total_sensores))
            
            # Contar registros de alertas
            cursor.execute("SELECT COUNT(*) FROM registros")
            total_alertas = cursor.fetchone()[0]
            self.lbl_alertas.configure(text=str(total_alertas))
            
            conn.close()