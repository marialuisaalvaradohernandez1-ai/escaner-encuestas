import pytesseract
from PIL import Image

imagen = Image.open("documento.jpg")

texto = pytesseract.image_to_string(
    imagen,
    lang="spa"
)

print(texto)


import re

texto = """
Nombre: Juan Pérez
Fecha: 15/08/2026
Teléfono: 6561234567
Correo: juan@gmail.com
"""

telefono = re.search(
    r'\b\d{10}\b',
    texto
)

correo = re.search(
    r'[\w\.-]+@[\w\.-]+\.\w+',
    texto
)

fecha = re.search(
    r'\b\d{2}/\d{2}/\d{4}\b',
    texto
)

print("Teléfono:", telefono.group() if telefono else "")
print("Correo:", correo.group() if correo else "")
print("Fecha:", fecha.group() if fecha else "")
