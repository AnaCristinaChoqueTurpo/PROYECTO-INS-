import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
import csv
import os
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

class Historial(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Título
        ctk.CTkLabel(self, text="Historial de Alertas (Registro Histórico)", font=("Arial", 24, "bold")).pack(pady=(0, 10), anchor="w")
        ctk.CTkLabel(self, text="Consulte y exporte los eventos registrados por el Nodo Coordinador.", font=("Arial", 14), text_color="gray").pack(anchor="w", pady=(0, 20))

        # --- PANEL DE FILTROS Y ACCIONES ---
        frame_top = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=10)
        frame_top.pack(fill="x", pady=(0, 10), padx=5)

        ctk.CTkLabel(frame_top, text="Filtrar por Nivel:", font=("Arial", 12)).pack(side="left", padx=(20, 10), pady=15)
        self.combo_filtro = ctk.CTkComboBox(frame_top, values=["Todos", "NORMAL", "PRECAUCIÓN", "PELIGRO"], command=self.cargar)
        self.combo_filtro.pack(side="left", padx=10, pady=15)

        ctk.CTkButton(frame_top, text="🔄 Recargar Tabla", width=120, command=self.cargar).pack(side="right", padx=10, pady=15)
        ctk.CTkButton(frame_top, text="📊 Generar Reporte Excel", width=180, fg_color="#1f538d", command=self.generar_excel).pack(side="right", padx=10, pady=15)

        # --- TABLA ESTILO PROFESIONAL ---
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b", font=("Arial", 11))
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1e1e1e", foreground="#00BFFF", font=("Arial", 12, "bold"), padding=10)

        columnas = ("ID", "Fecha y Hora", "Inclinación (°)", "Estado Registrado")
        self.tabla = ttk.Treeview(self, columns=columnas, show="headings", style="Treeview")
        
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Fecha y Hora", text="Fecha y Hora")
        self.tabla.heading("Inclinación (°)", text="Inclinación (°)")
        self.tabla.heading("Estado Registrado", text="Estado Registrado")

        self.tabla.column("ID", width=50, anchor="center")
        self.tabla.column("Fecha y Hora", width=200, anchor="center")
        self.tabla.column("Inclinación (°)", width=150, anchor="center")
        self.tabla.column("Estado Registrado", width=200, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)

        # Colores de las filas según el nivel
        self.tabla.tag_configure('rojo', foreground='#FF5555')
        self.tabla.tag_configure('amarillo', foreground='#FFD700')
        self.tabla.tag_configure('verde', foreground='#00FF00')

        self.cargar()

    def cargar(self, _=None):
        for item in self.tabla.get_children(): 
            self.tabla.delete(item)
            
        filtro = self.combo_filtro.get()
        
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            if filtro == "Todos":
                cursor.execute("SELECT id, fecha_hora, inclinacion, nivel_alerta FROM registros ORDER BY id DESC LIMIT 100")
            else:
                cursor.execute("SELECT id, fecha_hora, inclinacion, nivel_alerta FROM registros WHERE nivel_alerta=%s ORDER BY id DESC LIMIT 100", (filtro,))
            
            for fila in cursor.fetchall():
                nivel = fila[3]
                if "PELIGRO" in nivel: tag = 'rojo'
                elif "PRECAUCIÓN" in nivel: tag = 'amarillo'
                else: tag = 'verde'
                
                self.tabla.insert("", "end", values=fila, tags=(tag,))
            conn.close()

    def generar_excel(self):
        # 1. Pedir al usuario dónde guardar el archivo
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivos de Excel", "*.xlsx")],
            title="Guardar Reporte de Alertas",
            initialfile=f"Reporte_Alertas_{datetime.now().strftime('%Y%m%d')}.xlsx"
        )

        # Si el usuario cancela, salimos de la función
        if not ruta_guardado:
            return

        try:
            # 2. Obtener los datos de la base de datos
            conn = self.db.conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT id, fecha_hora, inclinacion, nivel_alerta FROM registros ORDER BY id DESC")
            datos = cursor.fetchall()
            conn.close()

            if not datos:
                messagebox.showwarning("Aviso", "No hay datos para exportar.")
                return

            # 3. Crear el archivo Excel con diseño profesional (openpyxl)
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte de Alertas"

            # Agregar un Título Grande
            ws.merge_cells('A1:D1')
            ws['A1'] = "REPORTE HISTÓRICO - SISTEMA DE ALERTA TEMPRANA"
            ws['A1'].font = Font(size=14, bold=True, color="FFFFFF")
            ws['A1'].fill = PatternFill(start_color="1F538D", end_color="1F538D", fill_type="solid")
            ws['A1'].alignment = Alignment(horizontal="center", vertical="center")

            # Encabezados de la tabla
            headers = ["ID", "Fecha y Hora", "Inclinación (°)", "Nivel de Alerta"]
            ws.append(headers)
            
            # Estilo de los encabezados
            for col_num, header in enumerate(headers, 1):
                cell = ws.cell(row=2, column=col_num)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="333333", end_color="333333", fill_type="solid")
                cell.alignment = Alignment(horizontal="center")

            # Insertar los datos
            for fila in datos:
                ws.append(fila)
                
                # Colorear la celda del nivel de alerta
                nivel = fila[3]
                row_num = ws.max_row
                if "PELIGRO" in nivel:
                    ws.cell(row=row_num, column=4).font = Font(color="FF0000", bold=True)
                elif "PRECAUCIÓN" in nivel:
                    ws.cell(row=row_num, column=4).font = Font(color="FFD700", bold=True)
                else:
                    ws.cell(row=row_num, column=4).font = Font(color="00AA00", bold=True)

            # Ajustar el ancho de las columnas
            ws.column_dimensions['A'].width = 10
            ws.column_dimensions['B'].width = 25
            ws.column_dimensions['C'].width = 20
            ws.column_dimensions['D'].width = 25

            # 4. Guardar el archivo
            wb.save(ruta_guardado)

            # 5. Abrir el archivo automáticamente en Excel
            os.startfile(ruta_guardado)
            
            messagebox.showinfo("Éxito", "El reporte en Excel se ha generado y abierto correctamente.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el reporte: {e}")