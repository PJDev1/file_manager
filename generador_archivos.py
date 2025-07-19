import os

n_serie1 = 'x234567890123456'
n_serie2 = 'y983874747476433'
n_serie3 = 'z823749394842737'
n_serie4 = 'w823749394842737'

lista = [n_serie1, n_serie2, n_serie3, n_serie4]

ruta = "C:/Users/Pedro/Pictures/DUMMY_PHOTOS"

os.makedirs(os.path.dirname(ruta), exist_ok=True)

for elemento in lista:
    cantidad_total = 51
    for i in range(1, cantidad_total):
        if(i < 10):
            name = f'{elemento}_00{i}'
        elif i >= 10 and i < 100:
            name = f'{elemento}_0{i}' 
        elif i >= 100:
            name = f'{elemento}_{i}'
    
            
        # with open(f'{ruta}/{elemento}_{i + 1}.jpg', "w") as f:
        with open(f'{ruta}/{name}.jpg', "w") as f:
            pass
    
print(f"Se crearon {(cantidad_total - 1) * len(lista)} de archivos en: {ruta}")