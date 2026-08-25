import os
from ocr import obtener_texto_ocr
from extractor_ia import extraer_con_ia
from database import guardar_en_db

def procesar_carpeta(ruta_carpeta):
    archivos = [f for f in os.listdir(ruta_carpeta) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    procesados = 0
    revision_requerida = 0
    
    for archivo in archivos:
        ruta_completa = os.path.join(ruta_carpeta, archivo)
        
        # 1. Aplicar OCR
        texto = obtener_texto_ocr(ruta_completa)
        
        # 2. Procesar con IA
        datos = extraer_con_ia(texto)
        
        # 3. Verificar umbral de confianza (ej. < 75% requiere revisión)
        confianza = datos.get("confianza", 0)
        estado = "OK" if confianza >= 75 else "REVISIÓN"
        
        if estado == "REVISIÓN":
            revision_requerida += 1
        
        # 4. Guardar en la Base de Datos
        guardar_en_db(
            nombre=datos.get("nombre"),
            telefono=datos.get("telefono"),
            fecha=datos.get("fecha"),
            correo=datos.get("correo"),
            confianza=confianza,
            estado=estado
        )
        
        procesados += 1
        print(f"[{procesados}/{len(archivos)}] {archivo} -> Confianza: {confianza}% ({estado})")

    print(f"\n✅ {procesados} documentos procesados")
    print(f"⚠️ {revision_requerida} documentos necesitan revisión")
