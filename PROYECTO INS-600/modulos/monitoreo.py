import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from datetime import datetime
import threading
import winsound
from tkinter import messagebox # <--- Necesario para el mensaje de silenciar

class Monitoreo(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        
        self.max_puntos = 30
        self.datos_inc = [0] * self.max_puntos
        self.datos_hum = [0] * self.max_puntos
        self.datos_llu = [0] * self.max_puntos
        
        self.alarma_activa = False

        ctk.CTkLabel(self, text="Dashboard Analítico - Nodo Coordinador", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")

        # --- PANEL SUPERIOR: TARJETAS Y LCD ---
        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.pack(fill="x", pady=10)

        # Tarjetas
        self.frame_stats = ctk.CTkFrame(frame_top, fg_color="transparent")
        self.frame_stats.pack(side="left", fill="x", expand=True)
        self.stats_inc = self.crear_tarjeta(self.frame_stats, "Inclinación", "0.0°", "#00BFFF")
        self.stats_hum = self.crear_tarjeta(self.frame_stats, "Humedad", "0%", "#00FF00")
        self.stats_llu = self.crear_tarjeta(self.frame_stats, "Lluvia", "0 mm", "#FFD700")

        # Pantalla LCD (Simula el hardware físico)
        self.lcd_frame = ctk.CTkFrame(frame_top, fg_color="#0a2a0a", corner_radius=10, width=200)
        self.lcd_frame.pack(side="right", padx=10, fill="y")
        self.lcd_frame.pack_propagate(False)
        self.lcd = ctk.CTkLabel(self.lcd_frame, text="ESTADO: ESPERA\nSIRENA: OFF", font=("Courier New", 14, "bold"), text_color="#00FF00")
        self.lcd.pack(expand=True)

        # --- GRÁFICA ---
        self.frame_grafica = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        self.frame_grafica.pack(fill="both", expand=True, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(8, 3), dpi=100)
        self.fig.patch.set_facecolor('#1e1e1e')
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.set_ylim(0, 12)
        
        self.linea_inc, = self.ax.plot([], [], color='#00BFFF', label='Inclinación (°)', linewidth=2)
        self.linea_hum, = self.ax.plot([], [], color='#00FF00', label='Humedad (%)', linewidth=2)
        self.linea_llu, = self.ax.plot([], [], color='#FFD700', label='Lluvia (mm)', linewidth=2, alpha=0.6)
        self.ax.legend(loc='upper right', facecolor='#1e1e1e', labelcolor='white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_grafica)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # --- PANEL INFERIOR ---
        frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        frame_bottom.pack(fill="x", pady=10)

        self.frame_ctrl = ctk.CTkFrame(frame_bottom, fg_color="#2b2b2b", corner_radius=10)
        self.frame_ctrl.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(self.frame_ctrl, text="Simulador de Sensores", font=("Arial", 14, "bold")).pack(pady=10)
        
        ctk.CTkLabel(self.frame_ctrl, text="Inclinación (°)").pack(anchor="w", padx=20)
        self.slider_inc = ctk.CTkSlider(self.frame_ctrl, from_=0, to=10, command=self.actualizar_datos)
        self.slider_inc.pack(padx=20, pady=(0, 10), fill="x")

        ctk.CTkButton(self.frame_ctrl, text="🚨 SIMULAR EMERGENCIA MÁXIMA", fg_color="#8B0000", hover_color="#FF0000", 
                      command=self.simular_panico).pack(pady=10, padx=20, fill="x")

        # --- CAMBIO CC-02: Botón de Silenciar ---
        self.btn_silenciar = ctk.CTkButton(self.frame_ctrl, text="🔇 SILENCIAR ALARMA", fg_color="#FF8C00", hover_color="#CC7000", 
                                           font=("Arial", 12, "bold"), command=self.silenciar_alarma)
        self.btn_silenciar.pack(pady=5, padx=20, fill="x")

        # Consola LoRa
        self.frame_lora = ctk.CTkFrame(frame_bottom, fg_color="#1a1a1a", corner_radius=10, width=350)
        self.frame_lora.pack(side="right", fill="both")
        self.frame_lora.pack_propagate(False)

        ctk.CTkLabel(self.frame_lora, text="📡 Consola LoRa (TX/RX)", font=("Arial", 12, "bold"), text_color="#00BFFF").pack(pady=5)
        self.txt_log = ctk.CTkTextbox(self.frame_lora, height=120, fg_color="#0a0a0a", text_color="#00FF00", font=("Courier New", 10))
        self.txt_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.txt_log.insert("0.0", "Iniciando módulo RAK3172...\nEsperando conexión con Nodos...\n")

    def crear_tarjeta(self, master, titulo, valor, color):
        card = ctk.CTkFrame(master, fg_color="#2b2b2b", corner_radius=10, height=90)
        card.pack(side="left", padx=5, fill="x", expand=True)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=("Arial", 12), text_color="gray").pack(pady=(15, 5))
        lbl = ctk.CTkLabel(card, text=valor, font=("Arial", 20, "bold"), text_color=color)
        lbl.pack()
        return lbl

    def simular_panico(self):
        self.slider_inc.set(8.5)
        self.actualizar_datos()

    def actualizar_datos(self, valor_manual=None):
        inc = valor_manual if valor_manual is not None else self.slider_inc.get()
        
        hum = random.randint(40, 95) if inc < 5 else random.randint(80, 100)
        llu = random.uniform(0, 5) if inc < 5 else random.uniform(8, 20)

        self.stats_inc.configure(text=f"{inc:.1f}°")
        self.stats_hum.configure(text=f"{int(hum)}%")
        self.stats_llu.configure(text=f"{llu:.1f} mm")

        hora = datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert("end", f"[{hora}] TX Nodo 1 -> Inc: {inc:.1f}°\n")
        self.txt_log.see("end")

        # Lógica y Sirena
        if inc >= 5.0 or hum >= 85 or llu >= 15.0:
            color = "#FF0000"
            self.lcd.configure(text="ESTADO: PELIGRO\nSIRENA: ON", text_color="#FF0000")
            self.txt_log.insert("end", f"[{hora}] 🚨 RX: PELIGRO - EVACUAR\n")
            self.db.guardar_alerta(inc, "PELIGRO")
            self.activar_sirena(True)
        elif inc >= 3.0 or hum >= 70 or llu >= 8.0:
            color = "#FFD700"
            self.lcd.configure(text="ESTADO: PRECAUCIÓN\nSIRENA: OFF", text_color="#FFD700")
            self.txt_log.insert("end", f"[{hora}] ⚠️ RX: PRECAUCIÓN\n")
            self.db.guardar_alerta(inc, "PRECAUCIÓN")
            self.activar_sirena(False)
        else:
            color = "#00FF00"
            self.lcd.configure(text="ESTADO: NORMAL\nSIRENA: OFF", text_color="#00FF00")
            self.activar_sirena(False)

        # Actualizar gráfica
        self.datos_inc.pop(0); self.datos_inc.append(inc)
        self.datos_hum.pop(0); self.datos_hum.append(hum)
        self.datos_llu.pop(0); self.datos_llu.append(llu)

        self.linea_inc.set_data(range(self.max_puntos), self.datos_inc)
        self.linea_hum.set_data(range(self.max_puntos), self.datos_hum)
        self.linea_llu.set_data(range(self.max_puntos), self.datos_llu)
        self.ax.set_xlim(0, self.max_puntos)
        self.ax.set_facecolor('#3a0d0d' if color == "#FF0000" else '#1e1e1e')
        self.canvas.draw()

        self.frame_ctrl.configure(fg_color=color if inc >= 5.0 else "#2b2b2b")

    def activar_sirena(self, estado):
        if estado and not self.alarma_activa:
            self.alarma_activa = True
            threading.Thread(target=self.reproducir_sonido, daemon=True).start()
        elif not estado:
            self.alarma_activa = False

    # --- CAMBIO CC-02: Función para silenciar ---
    def silenciar_alarma(self):
        self.alarma_activa = False
        messagebox.showinfo("Alarma Silenciada", "El sonido de la alarma se ha detenido.\nEl semáforo continuará en ROJO indicando el peligro.")

    def reproducir_sonido(self):
        while self.alarma_activa:
            winsound.Beep(1000, 400)
            winsound.Beep(1500, 400)