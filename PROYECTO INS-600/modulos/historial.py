import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import openpyxl
import csv

class Historial(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        ctk.CTkLabel(self, text="Historial de Alertas", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")

        # --- PANEL DE FILTROS (CON FECHAS) ---
        frame_filtros = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_filtros.pack(fill="x", pady=(0, 10), padx=5)

        # Filtro por Nivel
        ctk.CTkLabel(frame_filtros, text="Nivel:", font=("Arial", 12)).pack(side="left", padx=(10, 5), pady=15)
        self.combo_nivel = ctk.CTkComboBox(frame_filtros, values=["Todos", "NORMAL", "PRECAUCIÓN", "PELIGRO"], width=100)
        self.combo_nivel.pack(side="left", padx=5, pady=15)

        # Filtro por Fecha Inicial
        ctk.CTkLabel(frame_filtros, text="Desde:", font=("Arial", 12)).pack(side="left", padx=(15, 5), pady=15)
        self.entry_fecha_ini = ctk.CTkEntry(frame_filtros, width=100, placeholder_text="YYYY-MM-DD")
        self.entry_fecha_ini.pack(side="left", padx=5, pady=15)

        # Filtro por Fecha Final
        ctk.CTkLabel(frame_filtros, text="Hasta:", font=("Arial", 12)).pack(side="left", padx=(15, 5), pady=15)
        self.entry_fecha_fin = ctk.CTkEntry(frame_filtros, width=100, placeholder_text="YYYY-MM-DD")
        self.entry_fecha_fin.pack(side="left", padx=5, pady=15)

        # Botón Filtrar
        ctk.CTkButton(frame_filtros, text="🔍 Filtrar", width=80, command=self.cargar).pack(side="left", padx=15, pady=15)

        # Botones de Acción (Derecha)
        ctk.CTkButton(frame_filtros, text="📥 Exportar Excel", width=130, fg_color="#1f538d", command=self.generar_excel).pack(side="right", padx=10, pady=15)

        # --- TABLA ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="#00BFFF", font=("Arial", 12, "bold"))
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tabla = ttk.Treeview(self, columns=("ID", "Fecha", "Inclinación", "Nivel"), show="headings")
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Fecha", text="Fecha y Hora")
        self.tabla.heading("Inclinación", text="Inclinación (°)")
        self.tabla.heading("Nivel", text="Nivel de Alerta")
        
        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Fecha", width=200, anchor="center")
        self.tabla.column("Inclinación", width=150, anchor="center")
        self.tabla.column("Nivel", width=200, anchor="center")
        
        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)

        self.tabla.tag_configure('rojo', foreground='#FF5555')
        self.tabla.tag_configure('amarillo', foreground='#FFD700')
        self.tabla.tag_configure('verde', foreground='#00FF00')

        self.cargar()

    def cargar(self):
        for item in self.tabla.get_children(): 
            self.tabla.delete(item)
        
        nivel = self.combo_nivel.get()
        f_ini = self.entry_fecha_ini.get()
        f_fin = self.entry_fecha_fin.get()

        # Consulta SQL base
        query = "SELECT id, fecha_hora, inclinacion, nivel_alerta FROM registros WHERE 1=1"
        params = []

        if nivel != "Todos":
            query += " AND nivel_alerta LIKE %s"
            params.append(f"%{nivel}%")
        
        if f_ini:
            query += " AND DATE(fecha_hora) >= %s"
            params.append(f_ini)
        
        if f_fin:
            query += " AND DATE(fecha_hora) <= %s"
            params.append(f_fin)

        query += " ORDER BY id DESC LIMIT 100"

        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, tuple(params))
                for fila in cursor.fetchall():
                    tag = 'rojo' if "PELIGRO" in fila[3] else ('amarillo' if "PRECAUCIÓN" in fila[3] else 'verde')
                    self.tabla.insert("", "end", values=fila, tags=(tag,))
            except Exception as e:
                messagebox.showerror("Error de consulta", f"Error al filtrar: {e}")
            conn.close()

    def generar_excel(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx", 
            filetypes=[("Excel", "*.xlsx")], 
            title="Guardar Reporte de Alertas",
            initialfile=f"Reporte_Alertas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        )
        if not ruta: return
        
        try:
            conn = self.db.conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, fecha_hora, inclinacion, nivel_alerta FROM registros ORDER BY id DESC")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                messagebox.showwarning("Aviso", "No hay datos para exportar.")
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Alertas"
            
            ws.merge_cells('A1:D1')
            ws['A1'] = "REPORTE HISTÓRICO - SISTEMA DE ALERTA TEMPRANA"
            ws['A1'].font = openpyxl.styles.Font(size=14, bold=True, color="FFFFFF")
            ws['A1'].fill = openpyxl.styles.PatternFill(start_color="1F538D", end_color="1F538D", fill_type="solid")
            ws['A1'].alignment = openpyxl.styles.Alignment(horizontal="center", vertical="center")
            
            ws.append(["ID", "Fecha y Hora", "Inclinación (°)", "Nivel de Alerta"])
            
            for col_num, header in enumerate(["ID", "Fecha y Hora", "Inclinación (°)", "Nivel de Alerta"], 1):
                cell = ws.cell(row=2, column=col_num)
                cell.font = openpyxl.styles.Font(bold=True, color="FFFFFF")
                cell.fill = openpyxl.styles.PatternFill(start_color="333333", end_color="333333", fill_type="solid")
                cell.alignment = openpyxl.styles.Alignment(horizontal="center")

            for fila in datos:
                ws.append(fila)

            wb.save(ruta)
            os.startfile(ruta)
            messagebox.showinfo("Éxito", "Reporte Excel generado y abierto correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")