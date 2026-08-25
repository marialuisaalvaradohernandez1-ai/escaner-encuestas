import sqlite3

conexion = sqlite3.connect("documentos.db")

cursor = conexion.cursor()

cursor.execute("""
INSERT INTO documentos
(nombre, telefono, correo, fecha)
VALUES (?, ?, ?, ?)
""", (
    "Juan Pérez",
    "6561234567",
    "juan@gmail.com",
    "15/08/2026"
))

conexion.commit()
conexion.close()
