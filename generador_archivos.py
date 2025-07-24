import os
import numpy as np
from PIL import Image
import random

# --- Generar números de serie aleatorios ---
def generar_numero_serie():
    return ''.join(random.choices('0123456789ABCDEF', k=16))

# Crear una lista con 6 números de serie únicos
n_series = [generar_numero_serie() for _ in range(6)]

# Ruta de destino
ruta = "C:/Users/Pedro/Pictures/DUMMY_PHOTOS"
os.makedirs(ruta, exist_ok=True)

# Generar imágenes
for serie_index, serie in enumerate(n_series):
    for i in range(1, 16):  # 1 al 15
        nombre_archivo = f"{serie}_{i:03d}.jpg"
        ruta_archivo = os.path.join(ruta, nombre_archivo)

        # Crear imagen 50x50 con patrón distintivo
        data = np.full((50, 50), fill_value=((serie_index + 1) * i) % 256, dtype=np.uint8)
        imagen = Image.fromarray(data, mode="L")  # Escala de grises
        imagen.save(ruta_archivo, "JPEG")

print(f"Se generaron {15 * len(n_series)} imágenes reales en: {ruta}")
