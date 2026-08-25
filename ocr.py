import pytesseract
from PIL import Image

def obtener_texto_ocr(ruta_imagen):
    imagen = Image.open(ruta_imagen)
    texto = pytesseract.image_to_string(imagen, lang="spa")
    return texto
