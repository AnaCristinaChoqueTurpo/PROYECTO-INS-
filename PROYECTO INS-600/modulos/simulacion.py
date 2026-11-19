import customtkinter as ctk
import time
import threading

class Simulacion(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        
        # Título
        ctk.CTkLabel(self, text="Simulador de Escenario de Desastre", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Simule una emergencia real y observe la respuesta del sistema.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 20))

        # --- PANEL DE CONTROL ---
        frame_ctrl = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_ctrl.pack(fill="x", pady=10)

        self.btn_iniciar = ctk.CTkButton(frame_ctrl, text="▶ Iniciar Simulación de Deslizamiento", fg_color="#1f538d", font=("Arial", 14, "bold"), command=self.iniciar_simulacion)
        self.btn_iniciar.pack(side="left", padx=20, pady=20)

        self.btn_detener = ctk.CTkButton(frame_ctrl, text="⏹ Detener y Reiniciar", fg_color="#8B0000", command=self.detener_simulacion, state="disabled")
        self.btn_detener.pack(side="left", padx=10, pady=20)

        # --- ÁREA DE ESTADO (PANTALLA GRANDE) ---
        self.frame_estado = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_estado.pack(fill="both", expand=True, pady=10)

        # Textos de estado
        self.lbl_alerta = ctk.CTkLabel(self.frame_estado, text="SISTEMA EN ESPERA", font=("Arial", 32, "bold"), text_color="gray")
        self.lbl_alerta.pack(pady=(40, 10))

        self.lbl_info = ctk.CTkLabel(self.frame_estado, text="Presione 'Iniciar Simulación' para ver el protocolo.", font=("Arial", 16))
        self.lbl_info.pack(pady=10)

        # Pantalla tipo LCD
        self.lcd_frame = ctk.CTkFrame(self.frame_estado, fg_color="#0a2a0a", corner_radius=10, width=400, height=100)
        self.lcd_frame.pack(pady=20)
        self.lcd_frame.pack_propagate(False)
        self.lbl_lcd = ctk.CTkLabel(self.lcd_frame, text="SISTEMA: OK\nSIRENA: OFF", font=("Courier New", 18, "bold"), text_color="#00FF00")
        self.lbl_lcd.pack(expand=True)

        # Panel de acciones de la comunidad
        self.frame_acciones = ctk.CTkFrame(self.frame_estado, fg_color="transparent")
        self.frame_acciones.pack(pady=20)
        
        self.lbl_accion1 = ctk.CTkLabel(self.frame_acciones, text="", font=("Arial", 18, "bold"))
        self.lbl_accion1.pack(pady=5)
        self.lbl_accion2 = ctk.CTkLabel(self.frame_acciones, text="", font=("Arial", 18, "bold"))
        self.lbl_accion2.pack(pady=5)

        self.simulando = False

    def iniciar_simulacion(self):
        if not self.simulando:
            self.simulando = True
            self.btn_iniciar.configure(state="disabled")
            self.btn_detener.configure(state="normal")
            # Hilo para que la ventana no se congele
            threading.Thread(target=self.bucle_simulacion, daemon=True).start()

    def detener_simulacion(self):
        self.simulando = False
        self.btn_iniciar.configure(state="normal")
        self.btn_detener.configure(state="disabled")
        
        # Reiniciar pantalla
        self.lbl_alerta.configure(text="SISTEMA EN ESPERA", text_color="gray")
        self.lbl_info.configure(text="Simulación detenida. Puede iniciarla de nuevo.")
        self.lbl_lcd.configure(text="SISTEMA: OK\nSIRENA: OFF", text_color="#00FF00")
        self.lbl_accion1.configure(text="")
        self.lbl_accion2.configure(text="")
        self.frame_estado.configure(fg_color="#2b2b2b")

    def bucle_simulacion(self):
        # FASE 1: Condiciones Normales
        self.actualizar_pantalla("#00FF00", "FASE 1: CONDICIONES NORMALES", 
                                 "Inclinación: 1.2° | Humedad: 40% | Lluvia: 0 mm", 
                                 "☀️ Clima estable. La comunidad realiza sus actividades.", "")
        self.db.guardar_alerta(1.2, "NORMAL")
        time.sleep(4)
        if not self.simulando: return
        
        # FASE 2: Inicio de lluvias (Precaución)
        self.actualizar_pantalla("#FFD700", "FASE 2: LLUVIAS INTENSAS (PRECAUCIÓN)", 
                                 "Inclinación: 2.5° | Humedad: 75% | Lluvia: 8 mm", 
                                 "⚠️ El sistema detecta saturación del suelo.", 
                                 "👷 El técnico revisa los sensores y los paneles solares.")
        self.db.guardar_alerta(2.5, "PRECAUCIÓN")
        time.sleep(5)
        if not self.simulando: return

        # FASE 3: Deslizamiento Inminente (Peligro)
        self.actualizar_pantalla("#FF0000", "FASE 3: ¡PELIGRO INMINENTE!", 
                                 "Inclinación: 7.5° | Humedad: 98% | Lluvia: 18 mm", 
                                 "🚨 SIRENA ACTIVADA. LUCES ROJAS.", 
                                 "🏃‍♂️ PROTOCOLO DE EVACUACIÓN: La comunidad se dirige a zonas seguras.")
        self.db.guardar_alerta(7.5, "PELIGRO: EVACUAR")
        time.sleep(6)
        if not self.simulando: return

        # FASE 4: Fin de la simulación
        self.actualizar_pantalla("#00FF00", "SIMULACIÓN COMPLETADA", 
                                 "El sistema retorna a estado de monitoreo.", 
                                 "✅ La comunidad está a salvo.", "💡 Puede reiniciar la simulación.")
        self.detener_simulacion()

    def actualizar_pantalla(self, color, titulo, info, accion1, accion2):
        # Cambiar colores y textos
        self.lbl_alerta.configure(text=titulo, text_color=color)
        self.lbl_info.configure(text=info)
        self.lbl_accion1.configure(text=accion1, text_color=color)
        self.lbl_accion2.configure(text=accion2, text_color=color)
        
        # Cambiar el color del LCD
        estado_lcd = "NIVEL: PELIGRO\nSIRENA: ON" if color == "#FF0000" else "NIVEL: NORMAL\nSIRENA: OFF"
        self.lbl_lcd.configure(text=estado_lcd, text_color=color)
        
        # Cambiar el fondo del panel de estado
        self.frame_estado.configure(fg_color="#3a0d0d" if color == "#FF0000" else "#2b2b2b")