import mysql.connector

class BaseDatos:
    def __init__(self):
        self.config = {
            "host": "localhost", "user": "root", "password": "", "database": "sistema_deslizamientos"
        }

    def conectar(self):
        try:
            return mysql.connector.connect(**self.config)
        except:
            return None

    def validar_usuario(self, usuario, password):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario=%s AND password=%s", (usuario, password))
            res = cursor.fetchone()
            conn.close()
            return res is not None
        return False

    def guardar_alerta(self, inc, nivel):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO registros (inclinacion, nivel_alerta) VALUES (%s, %s)", (inc, nivel))
            conn.commit()
            conn.close()

    def obtener_historial(self):
        conn = self.conectar()
        datos = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fecha_hora, inclinacion, nivel_alerta FROM registros ORDER BY id DESC LIMIT 50")
            datos = cursor.fetchall()
            conn.close()
        return datos