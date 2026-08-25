import sqlite3

def guardar_en_db(nombre, telefono, fecha, correo, confianza, estado):
    conn = sqlite3.connect("documentos.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            telefono TEXT,
            fecha TEXT,
            correo TEXT,
            confianza INTEGER,
            estado TEXT
        )
    ''')
    
    cursor.execute('''
        INSERT INTO documentos (nombre, telefono, fecha, correo, confianza, estado)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, telefono, fecha, correo, confianza, estado))
    
    conn.commit()
    conn.close()
