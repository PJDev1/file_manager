import sys
import os
import shutil
import time
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QListWidget, QDateEdit,
    QGridLayout, QScrollArea, QDialog, QDesktopWidget
)
from PyQt5.QtCore import Qt, QDate, QDateTime, pyqtSignal
from PyQt5.QtGui import QPixmap
import datetime

# Global watcher variables
observer = None
observer_encendido = False
ruta_global = ""

def organizar_fotos(ruta):
    if not os.path.exists(ruta):
        print("La ruta no existe.")
        return

    # Obtener solo archivos (no carpetas), omitir ocultos
    photos = [
        f for f in os.listdir(ruta)
        if os.path.isfile(os.path.join(ruta, f)) and not f.startswith('.')
    ]

    fotos_por_serie = defaultdict(list)

    for photo in photos:
        if len(photo) < 16:
            continue
        numero_serie = photo[:16]
        fotos_por_serie[numero_serie].append(photo)

    for numero_serie, lista_fotos in fotos_por_serie.items():
        carpeta_serie = os.path.join(ruta, numero_serie)
        try:
            os.makedirs(carpeta_serie, exist_ok=True)
        except Exception as e:
            print(f"No pude crear la carpeta {carpeta_serie} - motivo: {e}")
            continue

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
            self.ui_ref.archivosNuevos.emit()
        except Exception as e:
            print(f"⚠️ Error moviendo archivo: {e}")

class ClickeableLabel(QLabel):
    dobleClick = pyqtSignal(str)
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path

    def mouseDoubleClickEvent(self, event):
        self.dobleClick.emit(self.path)

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os

class FullImageWindow(QDialog):
    def __init__(self, path_img):
        super().__init__()
        self.path_img = path_img
        self.setWindowTitle("Imagen completa — " + os.path.basename(path_img))

        # Obtengo el tamaño de la pantalla disponible (sin barra de tareas)
        screen_rect = QDesktopWidget().availableGeometry(self)
        max_w, max_h = screen_rect.width(), screen_rect.height()

        # Cargo la imagen original
        orig = QPixmap(self.path_img)
        # Escalo manteniendo aspecto dentro de la pantalla disponible
        scaled = orig.scaled(max_w, max_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Label con la imagen escalada
        label = QLabel()
        label.setPixmap(scaled)
        label.setAlignment(Qt.AlignCenter)

        # Layout y ajustes de tamaño
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # Redimensiono la ventana al tamaño de la imagen (más un pequeño margen)
        margin = 20
        self.resize(scaled.width() + margin, scaled.height() + margin)
        self.setWindowFlags(self.windowFlags() | Qt.Window)  # ventana normal, con marco
        self.move(
            screen_rect.left() + (max_w - self.width()) // 2,
            screen_rect.top()  + (max_h - self.height()) // 2
        )

class Modal(QWidget):
    def __init__(self, path_img):
        super().__init__()
        self.path_img = path_img

        self.setWindowTitle(os.path.basename(path_img))

        layout = QVBoxLayout()

        # Mostrar imagen
        if path_img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            pix = QPixmap(path_img).scaled(300, 300, Qt.KeepAspectRatio | Qt.SmoothTransformation)
            img_label = QLabel()
            img_label.setPixmap(pix)
            img_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(img_label)

         # Botón
        btnFullSize = QPushButton("Ver imagen completa")
        btnFullSize.clicked.connect(self.setFullSize)  # ✅ Conexión correcta
        layout.addWidget(btnFullSize)  # ✅ Añadir botón al layout

        # Mostrar metadatos
        if os.path.exists(path_img):
            stat = os.stat(path_img)
            size_kb = round(stat.st_size / 1024, 2)
            created = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            label_info = QLabel(f"""
            <p><b>Nombre:</b> {os.path.basename(path_img)}</p>
            <p><b>Tamaño:</b> {size_kb} KB</p>
            <p><b>Creado:</b> {created}</p>
            <p><b>Modificado:</b> {modified}</p>
            """)
            label_info.setTextFormat(Qt.RichText)
            label_info.setAlignment(Qt.AlignLeft)
            layout.addWidget(label_info)

        self.setLayout(layout)
        self.setFixedSize(400, 400)

    def setFullSize(self):
        full_window = FullImageWindow(self.path_img)
        full_window.exec_()

class UI(QWidget):
    archivosNuevos = pyqtSignal()
    def __init__(self, ruta):
        super().__init__()
        global ruta_global
        ruta_global = ruta
        self.archivosNuevos.connect(self.buscar, Qt.QueuedConnection)
        self.setWindowTitle("Clasificador de imágenes")
        self.setGeometry(100, 100, 900, 700)
        self._modals = []  # Para guardar referencias a modales
        # Estilos
        self.setStyleSheet("""
            QLabel { font-size: 16px; }
            QComboBox, QLineEdit, QPushButton, QDateEdit { font-size: 14px; }
        """ )
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        # Ruta y monitor
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
        # Filtros
        fila_layout = QHBoxLayout()
        self.buscar_label = QLabel("Ingrese su búsqueda")
        self.busqueda_input = QLineEdit()
        self.combo = QComboBox(); self.combo.addItems(["Nombre", "Fecha"]);
        self.combo.currentTextChanged.connect(self.filtro_cambiado)
        self.date_from = QDateEdit(calendarPopup=True); self.date_from.setDate(QDate.currentDate().addMonths(-1)); self.date_from.setEnabled(False)
        self.date_to = QDateEdit(calendarPopup=True); self.date_to.setDate(QDate.currentDate()); self.date_to.setEnabled(False)
        self.btn_buscar = QPushButton("Buscar"); self.btn_buscar.clicked.connect(self.buscar)
        fila_layout.addWidget(self.buscar_label)
        fila_layout.addWidget(self.busqueda_input)
        fila_layout.addWidget(self.combo)
        fila_layout.addWidget(self.date_from)
        fila_layout.addWidget(self.date_to)
        fila_layout.addWidget(self.btn_buscar)
        main_layout.addLayout(fila_layout)
        # Estado
        self.estado_monitor_label = QLabel()
        self.estado_resultados_label = QLabel()
        main_layout.addWidget(self.estado_monitor_label)
        main_layout.addWidget(self.estado_resultados_label)
        # Contenedores: carpetas y archivos
        fila2_layout = QHBoxLayout()
        # Carpetas
        contenedor_carpetas = QWidget()
        contenedor_carpetas.setFixedWidth(300)
        carpetas_layout = QVBoxLayout(contenedor_carpetas)
        carpetas_layout.addWidget(QLabel("Números de serie:"))
        self.lista_carpetas = QListWidget(); self.lista_carpetas.itemSelectionChanged.connect(self.mostrar_archivos_carpeta)
        carpetas_layout.addWidget(self.lista_carpetas)
        fila2_layout.addWidget(contenedor_carpetas)
        # Archivos
        contenedor_archivos = QWidget()
        archivos_layout = QVBoxLayout(contenedor_archivos)
        archivos_layout.addWidget(QLabel("Fotografías:"))
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True)
        self.widget_contenedor = QWidget(); self.grid_archivos = QGridLayout(self.widget_contenedor)
        self.scroll_area.setWidget(self.widget_contenedor)
        archivos_layout.addWidget(self.scroll_area)
        fila2_layout.addWidget(contenedor_archivos)
        main_layout.addLayout(fila2_layout)
        # Iniciar
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
        if encendido: self.activar_watcher()
        else: self.desactivar_watcher()

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
                if (filtro == "Nombre" and texto in entry.lower()) or \
                   (filtro == "Fecha" and QDateTime.fromSecsSinceEpoch(int(os.path.getmtime(full_path))).date() in [self.date_from.date(), self.date_to.date()]):
                    carpetas.append(entry)
        self.lista_carpetas.clear()
        self.limpiar_grid_archivos()
        self.lista_carpetas.addItems(carpetas)
        self.set_estado_resultados(f"Encontradas {len(carpetas)} carpetas")
    def limpiar_grid_archivos(self):
        while self.grid_archivos.count():
            item = self.grid_archivos.takeAt(0)
            w = item.widget()
            if w: w.setParent(None)

    def mostrar_archivos_carpeta(self):
        items = self.lista_carpetas.selectedItems()
        self.limpiar_grid_archivos()
        if not items: return
        carpeta = items[0].text()
        path_c = os.path.join(ruta_global, carpeta)
        if not os.path.exists(path_c): return
        archivos = [f for f in os.listdir(path_c) if os.path.isfile(os.path.join(path_c, f))]
        archivos.sort()
        cols = 3; row = col = 0
        for archivo in archivos:
            path_img = os.path.join(path_c, archivo)
            cont = QWidget(); lay = QVBoxLayout(cont)
            pix = QPixmap(path_img).scaled(100,100,Qt.KeepAspectRatio)
            label = ClickeableLabel(path_img, parent=self)
            label.setPixmap(pix); label.setAlignment(Qt.AlignCenter)
            label.dobleClick.connect(self.mostrar_datos_archivo)
            name = QLabel(archivo); name.setAlignment(Qt.AlignCenter)
            lay.addWidget(label); lay.addWidget(name)
            self.grid_archivos.addWidget(cont, row, col)
            col += 1
            if col >= cols: col = 0; row += 1

    def mostrar_datos_archivo(self, path_img):
        if not os.path.exists(path_img): return
        modal = Modal(path_img)
        modal.setWindowModality(Qt.ApplicationModal)
        modal.show()
        self._modals.append(modal)
    def filtro_cambiado(self, texto):
        self.date_from.setEnabled(texto=="Fecha")
        self.date_to.setEnabled(texto=="Fecha")
        self.busqueda_input.setEnabled(texto=="Nombre")
    def set_estado_monitor(self, msg, error=False):
        color = 'red' if error else ('green' if observer_encendido else 'gray')
        self.estado_monitor_label.setText(msg)
        self.estado_monitor_label.setStyleSheet(f'color: {color}')
    def set_estado_resultados(self, msg):
        self.estado_resultados_label.setText(msg)
    def closeEvent(self, event):
        global observer
        if observer: observer.stop(); observer.join()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ruta = sys.argv[1] if len(sys.argv)>1 else os.path.expanduser('~/Documents/prueba_fotos')
    win = UI(ruta)
    win.show()
    sys.exit(app.exec_())
