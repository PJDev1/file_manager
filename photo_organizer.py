import os
import shutil

ruta = "C:/Users/Pedro/Pictures/DUMMY_PHOTOS"
photos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]

ruta_destino = "./organized_photos"

if not(os.path.exists(ruta_destino)):
    os.mkdir(ruta_destino)
else:
    print(f"Los archivos se guardaran en la siguiente direccion:{ruta_destino}")

def obtenerNumerosDeSerie():
    nums_serie = [] 
    for photo in photos:
        n_serie = photo[0:16]
        if n_serie not in nums_serie:
            nums_serie.append(n_serie)
            
    # print(nums_serie)
    return nums_serie
    
def crearDirectorio(numeros_serie):
    for n_serie in numeros_serie:
        carpeta_motor = f'./{ruta_destino}/{n_serie}'
        if not(os.path.exists(carpeta_motor)):
            os.mkdir(carpeta_motor)

def crearListaPorNumeroDeSerie(numeros_serie):
    diccionario = {numero_de_serie: [] for numero_de_serie in numeros_serie}
    print(diccionario)
    return diccionario

def buscarPorNumeroDeSerie(photos, numeros_de_serie):
    total = 0
    numero_de_lista = 1
    for photo in photos:
        for clave in numeros_de_serie:
            if photo[0:16] == clave:
                # print(f'{photo} = {clave}')
                numeros_de_serie[clave].append(photo)
                if len(numeros_de_serie[clave]) == 15:
                    print(f"La lista {numero_de_lista} {numeros_de_serie[clave]} tiene: {len(numeros_de_serie[clave])} elementos")
                    total += len(numeros_de_serie[clave])
                    numero_de_lista += 1 
    print("Total de archivos:", total)
                    
    return numeros_de_serie
        
    

numeros_de_serie = obtenerNumerosDeSerie()
crearDirectorio(numeros_de_serie)
diccionario = crearListaPorNumeroDeSerie(numeros_de_serie)

main_counter = 0

while main_counter < len(photos):
    print(f'{main_counter}: {len(photos)}')
    buscarPorNumeroDeSerie(photos, diccionario)
    main_counter += 1


# for i, photo in enumerate(photos):
#     n_serie = photo[0:16]
    
#     if(n_serie not in nums_serie):
#         nums_serie.append(n_serie)
        
#     if(len(n_serie) > 16 or len(n_serie) < 16):
#         print("El numero de serie tiene mas de 16 digitos")
#         print("Verifique el numero de serie")
#     else:
#         #Directorio por motor 
#         carpeta_motor = f'./{ruta_destino}/{n_serie}'

#         if not(os.path.exists(carpeta_motor)):
#             os.mkdir(carpeta_motor)
            
#         for i in range(0, len(photos), 15):
#             # lote = photos[i:i+14]  # Obtener 15 elementos (o menos si es el final)
            
#             subcarpeta_motor = f'./{carpeta_motor}/{n_serie}_{i//15 + 1}'

#             #Subdirectorio que almacenara cada 15 fotos    
#             if not(os.path.exists(subcarpeta_motor)):
#                 os.mkdir(subcarpeta_motor)
                
#             for num_serie in nums_serie:
#                 n_serie_photo = photo[0:16]
#                 print(f'Comparando: {n_serie_photo} con {num_serie}')
#                 if num_serie == n_serie_photo:
#                     print(f'{num_serie} = {n_serie}')
#                     print(f'Se agregara la foto: {photo[:]}')
#                     lote.append(photo[:])
                

#         print(f'Lote {i//15 + 1}: {lote}')
#         print(f'Tamanio del Lote: {len(lote)}')
                
            
#             # origen = f'{ruta}/{foto}'
#             # destino = f'{subcarpeta_motor}/{foto}'
#             # print(f'Moviendo: {origen} -> {destino}')
#             # shutil.copy2(origen, subcarpeta_motor)
            
#             # Aquí haces lo que necesites con el lote de 15 elementos
#             # print(f"Procesando lote {i//15 + 1}: {lote}")
            
            
            

        
            
            
                

                
            

        
         
            
        
    



