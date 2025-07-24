import sys
import os
import shutil
import time
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QListWidget, QDateEdit
)
from PyQt5.QtCore import Qt, QDate, QDateTime, pyqtSignal
from PyQt5.QtGui import QPixmap
import datetime

observer = None
observer_encendido = False
ruta_global = ""

def organizar_fotos(ruta):
    if not os.path.exists(ruta):
        print("La ruta no existe.")
        return

    photos = [f for f in os.listdir(ruta) if os.path.isfile(os.path.join(ruta, f))]
    fotos_por_serie = defaultdict(list)

    for photo in photos:
        numero_serie = photo[0:16]
        fotos_por_serie[numero_serie].append(photo)

    for numero_serie, lista_fotos in fotos_por_serie.items():
        carpeta_serie = os.path.join(ruta, numero_serie)
        os.makedirs(carpeta_serie, exist_ok=True)
        for foto in lista_fotos:
            origen = os.path.join(ruta, foto)
            destino = os.path.join(carpeta_serie, foto)
            print(f'{origen} -> {destino}')
            try:
                shutil.move(origen, destino)
            except Exception as e:
                print("No pude mover:", origen, "- motivo:", e)

class MiHandler(FileSystemEventHandler):
    def __init__(self, ui_ref):
        super().__init__()
        self.ui_ref = ui_ref

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = event.src_path
        # Espera a que el archivo tenga contenido
        for _ in range(10):
            try:
                if os.path.getsize(file_path) > 0:
                    break
            except OSError:
                pass
            time.sleep(0.1)

        try:
            numero_serie = os.path.basename(file_path)[:16]
            carpeta_destino = os.path.join(ruta_global, numero_serie)
            os.makedirs(carpeta_destino, exist_ok=True)
            destino = os.path.join(carpeta_destino, os.path.basename(file_path))
            shutil.move(file_path, destino)
            print(f"📁 Movido automáticamente: {file_path} -> {destino}")
            # Emitir señal al hilo principal
            self.ui_ref.archivosNuevos.emit()
        except Exception as e:
            print(f"⚠️ Error moviendo archivo: {e}")

class UI(QWidget):
    archivosNuevos = pyqtSignal()

    def __init__(self, ruta):
        super().__init__()
        global ruta_global
        ruta_global = ruta

        # Conectar señal a slot buscar()
        self.archivosNuevos.connect(self.buscar, Qt.QueuedConnection)

        self.setStyleSheet("""
            QLabel {
                font-size: 16px;
            }
            QComboBox, QLineEdit, QPushButton, QDateEdit {
                font-size: 14px;
            }
        """
        )

        self.setWindowTitle("Clasificador de imágenes")
        self.setGeometry(100, 100, 900, 700)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # Ruta y botón monitor
        ruta_layout = QHBoxLayout()
        self.ruta_label = QLabel("Ruta:")
        self.ruta_input = QLineEdit(ruta_global)
        self.ruta_input.setReadOnly(True)
        self.btn_toggle_monitor = QPushButton("Encender Monitor")
        self.btn_toggle_monitor.clicked.connect(self.on_btn_toggle_monitor_clicked)
        ruta_layout.addWidget(self.ruta_label)
        ruta_layout.addWidget(self.ruta_input)
        ruta_layout.addWidget(self.btn_toggle_monitor)
        main_layout.addLayout(ruta_layout)

        # Búsqueda y filtros
        fila_layout = QHBoxLayout()
        self.buscar_label = QLabel("Ingrese su búsqueda")
        self.busqueda_input = QLineEdit()
        self.combo = QComboBox()
        self.combo.addItems(["Nombre", "Fecha"])
        self.combo.currentTextChanged.connect(self.filtro_cambiado)
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setEnabled(False)
        self.date_to = QDateEdit(calendarPopup=True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setEnabled(False)
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar)
        fila_layout.addWidget(self.buscar_label)
        fila_layout.addWidget(self.busqueda_input)
        fila_layout.addWidget(self.combo)
        fila_layout.addWidget(self.date_from)
        fila_layout.addWidget(self.date_to)
        fila_layout.addWidget(self.btn_buscar)
        main_layout.addLayout(fila_layout)

        # Estado monitor & resultados
        self.estado_monitor_label = QLabel()
        self.estado_resultados_label = QLabel()
        main_layout.addWidget(self.estado_monitor_label)
        main_layout.addWidget(self.estado_resultados_label)

        # Listas y preview
        fila2_layout = QHBoxLayout()
        # Carpetas
        carpeta_layout = QVBoxLayout()
        carpeta_layout.addWidget(QLabel("Números de serie:"))
        self.lista_carpetas = QListWidget()
        self.lista_carpetas.itemSelectionChanged.connect(self.mostrar_archivos_carpeta)
        carpeta_layout.addWidget(self.lista_carpetas)
        fila2_layout.addLayout(carpeta_layout)
        # Archivos
        archivo_layout = QVBoxLayout()
        archivo_layout.addWidget(QLabel("Archivos:"))
        self.lista_archivos = QListWidget()
        self.lista_archivos.itemSelectionChanged.connect(self.mostrar_datos_archivo)
        archivo_layout.addWidget(self.lista_archivos)
        fila2_layout.addLayout(archivo_layout)
        main_layout.addLayout(fila2_layout)

        # Preview contenedor
        preview_layout = QHBoxLayout()
        self.preview_image = QLabel()
        self.preview_image.setFixedSize(150, 150)
        preview_layout.addWidget(self.preview_image)
        self.data = QLabel()
        self.data.setWordWrap(True)
        preview_layout.addWidget(self.data)
        main_layout.addLayout(preview_layout)

        self.setLayout(main_layout)
        # Arrancar watcher y mostrar carpetas
        self.toggle_monitor(True)
        self.buscar()

    def activar_watcher(self):
        global observer, observer_encendido
        if observer is None:
            organizar_fotos(ruta_global)
            observer_encendido = True
            observer = Observer()
            handler = MiHandler(self)
            observer.schedule(handler, path=ruta_global, recursive=True)
            observer.start()
            self.btn_toggle_monitor.setText("Apagar Monitoreo")
            self.set_estado_monitor("Monitor Encendido")

    def desactivar_watcher(self):
        global observer, observer_encendido
        if observer:
            observer_encendido = False
            observer.stop()
            observer.join()
            observer = None
            self.btn_toggle_monitor.setText("Encender Monitoreo")
            self.set_estado_monitor("Monitor Apagado")

    def toggle_monitor(self, encendido):
        if encendido:
            self.activar_watcher()
        else:
            self.desactivar_watcher()

    def on_btn_toggle_monitor_clicked(self):
        global observer_encendido
        self.toggle_monitor(not observer_encendido)

    def buscar(self):
        texto = self.busqueda_input.text().lower()
        filtro = self.combo.currentText()

        carpetas = []
        for entry in os.listdir(ruta_global):
            full_path = os.path.join(ruta_global, entry)
            if os.path.isdir(full_path):
                if filtro == "Nombre":
                    if texto in entry.lower():
                        carpetas.append(entry)
                elif filtro == "Fecha":
                    mod_time = os.path.getmtime(full_path)
                    fecha_mod = QDateTime.fromSecsSinceEpoch(int(mod_time)).date()
                    desde = self.date_from.date()
                    hasta = self.date_to.date()
                    if desde <= fecha_mod <= hasta:
                        carpetas.append(entry)
                else:
                    carpetas.append(entry)

        self.lista_carpetas.clear()
        self.lista_archivos.clear()
        self.lista_carpetas.addItems(carpetas)

        self.set_estado_resultados(f"Encontradas {len(carpetas)} carpetas")

    def mostrar_archivos_carpeta(self):
        selected = self.lista_carpetas.selectedItems()
        self.lista_archivos.clear()
        if not selected: return
        carpeta = selected[0].text()
        path_c = os.path.join(ruta_global, carpeta)
        if not os.path.exists(path_c): return
        archivos = [f for f in os.listdir(path_c) if os.path.isfile(os.path.join(path_c, f))]
        self.lista_archivos.addItems(archivos)

    def mostrar_datos_archivo(self):
        sel_files = self.lista_archivos.selectedItems()
        sel_carp = self.lista_carpetas.selectedItems()
        if not sel_files or not sel_carp: return
        archivo = sel_files[0].text()
        carpeta = sel_carp[0].text()
        path_f = os.path.join(ruta_global, carpeta, archivo)
        if not os.path.exists(path_f): return
        stat = os.stat(path_f)
        size_kb = round(stat.st_size/1024,2)
        created = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        self.data.setText(f"Nombre:{archivo}\nTamaño:{size_kb} KB\nCreado:{created}\nModificado:{modified}")
        if archivo.lower().endswith(('.png','.jpg','.jpeg','.gif','.bmp')):
            pix = QPixmap(path_f).scaled(150,150,Qt.KeepAspectRatio,Qt.SmoothTransformation)
            self.preview_image.setPixmap(pix)
        else:
            self.preview_image.clear()

    def filtro_cambiado(self, texto):
        if texto == "Fecha":
            self.date_from.setEnabled(True)
            self.date_to.setEnabled(True)
            self.busqueda_input.setEnabled(False)
        else:
            self.busqueda_input.setEnabled(True)
            self.date_from.setEnabled(False)
            self.date_to.setEnabled(False)

    def set_estado_monitor(self, msg, error=False):
        color = 'red' if error else ('green' if observer_encendido else 'gray')
        self.estado_monitor_label.setText(msg)
        self.estado_monitor_label.setStyleSheet(f'color: {color}')

    def set_estado_resultados(self, msg):
        self.estado_resultados_label.setText(msg)

    def closeEvent(self, event):
        global observer
        if observer:
            observer.stop()
            observer.join()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ruta = r"C:/Users/Pedro/Pictures/DUMMY_PHOTOS"
    ventana = UI(ruta)
    ventana.show()
    sys.exit(app.exec_())
