import sqlite3
import pandas as pd

conexion = sqlite3.connect("documentos.db")

df = pd.read_sql_query(
    "SELECT * FROM documentos",
    conexion
)

df.to_excel(
    "documentos.xlsx",
    index=False
)

conexion.close()

print("Excel creado correctamente.")
