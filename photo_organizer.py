import os
import shutil
from collections import defaultdict

# Rutas
ruta = "C:/Users/Pedro/Pictures/DUMMY_PHOTOS"
ruta_destino = "./organized_photos"

# Obtener todos los archivos en la carpeta
photos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]

# Crear carpeta raíz si no existe
if not os.path.exists(ruta_destino):
    os.mkdir(ruta_destino)
else:
    print(f"Los archivos se guardarán en: {ruta_destino}")

# Agrupar fotos por número de serie
fotos_por_serie = defaultdict(list)
for photo in photos:
    numero_serie = photo[0:16]
    fotos_por_serie[numero_serie].append(photo)

# Crear carpetas y mover archivos por bloques de 15
for numero_serie, lista_fotos in fotos_por_serie.items():
    # Crear carpeta principal por número de serie
    carpeta_serie = os.path.join(ruta_destino, numero_serie)
    os.makedirs(carpeta_serie, exist_ok=True)

    # Dividir en bloques de 15
    for i in range(0, len(lista_fotos), 15):
        bloque = lista_fotos[i:i+15]
        subcarpeta = os.path.join(carpeta_serie, f"{numero_serie}_{i//15 + 1}")
        os.makedirs(subcarpeta, exist_ok=True)

        for foto in bloque:
            origen = os.path.join(ruta, foto)
            destino = os.path.join(subcarpeta, foto)
            shutil.move(origen, destino)  # o shutil.copy2() si no quieres mover

        print(f"📁 {subcarpeta} -> {len(bloque)} archivos")

print(f"Total de archivos procesados: ")

print("✅ Organización completada.")
