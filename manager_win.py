from PyQt5.QtWidgets import (
    QLineEdit, QVBoxLayout, QWidget, QPushButton, QListWidget, QLabel, QHBoxLayout, QTabWidget, QTabBar
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QFontMetrics, QPainterPath, QImage, QBrush
from PyQt5.QtCore import Qt, QTimer, QRectF
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica
from worker_manager import WorkerManager
from styles import get_common_styles
from class_win import ClassWindow


class ManagerWindow(ClassWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.set_window_size_absolute(1280, 720)
        self.setStyleSheet(get_common_styles())

        self.manager = WorkerManager()

        # Temporizadores para búsquedas
        self.timer_busqueda_codigo = QTimer()
        self.timer_busqueda_codigo.setSingleShot(True)
        self.timer_busqueda_codigo.timeout.connect(self.buscar_por_codigo)

        self.timer_busqueda_nombre = QTimer()
        self.timer_busqueda_nombre.setSingleShot(True)
        self.timer_busqueda_nombre.timeout.connect(self.buscar_por_nombre)

        # Layout principal
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.West)  # Coloca las pestañas a la izquierda con west btw, sino se ponen verticales....

        # Crear la pestaña de gestión de productos
        self.producto_tab = QWidget()
        self.tab_widget.addTab(self.producto_tab, "Gestión de Productos")

        self.home_tab = self.create_home_tab()
        self.tab_widget.addTab(self.home_tab, "Inicio")

        self.producto_layout = QVBoxLayout(self.producto_tab)

        
        # Input de código de barras
        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')
        self.codigo_barras_input.textChanged.connect(self.iniciar_timer_codigo)

        # Input de nombre
        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText('Nombre del Producto')
        self.nombre_input.textChanged.connect(self.iniciar_timer_nombre)

        # Input de cantidad
        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText('Cantidad')

        # Botones
        self.agregar_button = QPushButton('Agregar Producto', self)
        self.agregar_button.setObjectName('agregar_button')
        self.agregar_button.clicked.connect(self.agregar_producto)

        self.modificar_button = QPushButton('Modificar Producto', self)
        self.modificar_button.setObjectName('modificar_button')
        self.modificar_button.clicked.connect(self.modificar_producto)

        # Listas para mostrar resultados
        self.resultados_codigo_label = QLabel("Resultados por Código:")
        self.resultados_codigo_label.setStyleSheet("font-weight: bold;")
        self.resultados_codigo_list = QListWidget(self)

        self.resultados_nombre_label = QLabel("Resultados por Nombre:")
        self.resultados_nombre_label.setStyleSheet("font-weight: bold;")
        self.resultados_nombre_list = QListWidget(self)

        self.producto_list = QListWidget(self)  # Lista para mostrar productos
        self.producto_layout.addWidget(self.codigo_barras_input)
        self.producto_layout.addWidget(self.nombre_input)
        self.producto_layout.addWidget(self.cantidad_input)
        self.producto_layout.addWidget(self.agregar_button)
        self.producto_layout.addWidget(self.modificar_button)

        
        # Agregar el tab widget al layout principal
        self.layout = QHBoxLayout() 
        self.layout.addWidget(self.tab_widget) 
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.layout)  # Configura el layout del widget central!!

        # Agregar elementos al layout de resultados
        self.layout_resultados = QVBoxLayout()
        self.layout_resultados.addWidget(self.resultados_codigo_label)
        self.layout_resultados.addWidget(self.resultados_codigo_list)
        self.layout_resultados.addWidget(self.resultados_nombre_label)
        self.layout_resultados.addWidget(self.resultados_nombre_list)

        self.layout.addLayout(self.layout_resultados)

        # Configurar el contenedor final
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def create_home_tab(self):
        """Crea la pestaña principal del dashboard."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Header de usuario
        user_info_layout = QHBoxLayout()
        avatar = QLabel()
        avatar.setPixmap(self.create_circular_pixmap("profile_pic.jpg", 100))
        user_info_layout.addWidget(avatar)

        user_details = QVBoxLayout()
        user_name = QLabel("Usuario: eliiin")
        user_name.setFont(QFont("Arial", 16, QFont.Bold))

        # para añadir widget se utiliza esto por ejemplo:
        # user_details.addWidget(QLabel())
        # example: user_level = QLabel("Nivel: mi opene")

        user_details.addWidget(user_name)
        
        user_info_layout.addLayout(user_details)
        user_info_layout.addStretch()

        layout.addLayout(user_info_layout)

        # Sección de configuraciones rápidas
        quick_settings_layout = QVBoxLayout()
        quick_settings_label = QLabel("Configuraciones Rápidas")
        quick_settings_label.setFont(QFont("Arial", 14, QFont.Bold))
        quick_settings_layout.addWidget(quick_settings_label)

        light_mode_btn = QPushButton("Modo Claro")
        dark_mode_btn = QPushButton("Modo Oscuro")
        restart_btn = QPushButton("Reiniciar Explorador")
        quick_settings_layout.addWidget(light_mode_btn)
        quick_settings_layout.addWidget(dark_mode_btn)
        quick_settings_layout.addWidget(restart_btn)

        layout.addLayout(quick_settings_layout)
        tab.setLayout(layout)

        return tab
        
    def create_circular_pixmap(self, path, diameter):
        """Crea un QPixmap circular!!!1!!!1!!"""
        original_pixmap = QPixmap(path)
        size = min(original_pixmap.width(), original_pixmap.height())
        rect = QRectF(0, 0, size, size)

        image = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
        image.fill(Qt.transparent)

        painter = QPainter(image)
        path = QPainterPath()
        path.addEllipse(rect)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, original_pixmap)
        painter.end()

        pixmap = QPixmap.fromImage(image)
        return pixmap.scaled(diameter, diameter, Qt.KeepAspectRatio, Qt.SmoothTransformation)


    def iniciar_timer_codigo(self):
        """Reinicia el temporizador para buscar por código de barras."""
        self.timer_busqueda_codigo.start(1)  # Segundos de delay en milisegundos

    def iniciar_timer_nombre(self):
        """Reinicia el temporizador para buscar por nombre."""
        self.timer_busqueda_nombre.start(1)  # Lo mismo que lo de arriba we

    def buscar_por_codigo(self):
        """Inicia un hilo para buscar el producto por código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        if codigo_barras:
            self.manager.ejecutar_worker(
                func=buscar_producto_logica,
                op_type='buscar_codigo',
                resultado_callback=self.mostrar_resultados_codigo,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras
            )

    def buscar_por_nombre(self):
        """Inicia un hilo para buscar productos por nombre."""
        nombre = self.nombre_input.text()
        if nombre:
            self.manager.ejecutar_worker(
                func=buscar_productos_por_nombre_logica,
                op_type='buscar_nombre',
                resultado_callback=self.mostrar_resultados_nombre,
                error_callback=self.mostrar_error,
                nombre=nombre
            )

    def mostrar_resultados_codigo(self, producto, op_type):
        """Muestra los resultados de búsqueda por código en la lista."""
        self.resultados_codigo_list.clear()
        if producto:
            self.resultados_codigo_list.addItem(f"{producto['codigo_barras']} - {producto['nombre']} ({producto['cantidad']})")
        else:
            self.resultados_codigo_list.addItem("Producto no encontrado.")

    def mostrar_resultados_nombre(self, productos, op_type):
        """Muestra los resultados de búsqueda por nombre en la lista."""
        self.resultados_nombre_list.clear()
        if productos:
            for producto in productos:
                self.resultados_nombre_list.addItem(f"{producto['codigo_barras']} - {producto['nombre']}")
        else:
            self.resultados_nombre_list.addItem("No se encontraron productos.")

    def agregar_producto(self):
        """Lógica para agregar productos."""
        codigo_barras = self.codigo_barras_input.text()
        nombre = self.nombre_input.text()
        try:
            cantidad = int(self.cantidad_input.text())
            self.manager.ejecutar_worker(
                func=crear_producto_logica,
                op_type='crear_producto',
                resultado_callback=self.mostrar_mensaje_exito,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras,
                nombre=nombre,
                cantidad=cantidad
            )
        except ValueError:
            self.mostrar_error("Cantidad inválida.", "crear_producto")

    def modificar_producto(self):
        """Lógica para modificar productos."""
        codigo_barras = self.codigo_barras_input.text()
        nombre = self.nombre_input.text()
        try:
            cantidad = int(self.cantidad_input.text())
            self.manager.ejecutar_worker(
                func=modificar_producto_logica,
                op_type='modificar_producto',
                resultado_callback=self.mostrar_mensaje_exito,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras,
                nombre=nombre,
                cantidad=cantidad
            )
        except ValueError:
            self.mostrar_error("Cantidad inválida.", "modificar_producto")

    def mostrar_mensaje_exito(self, resultado, op_type):
        """Actualiza la interfaz para indicar éxito."""
        if op_type == 'crear_producto':
            self.resultados_codigo_list.addItem("Producto agregado correctamente.")
        elif op_type == 'modificar_producto':
            self.resultados_codigo_list.addItem("Producto modificado correctamente.")
        self.limpiar_formulario()

    def mostrar_error(self, error, op_type):
        """Muestra el error directamente en los resultados."""
        if op_type == 'crear_producto' or op_type == 'modificar_producto':
            self.resultados_codigo_list.addItem(f"Error: {error}")
        else:
            self.resultados_nombre_list.addItem(f"Error: {error}")

    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.codigo_barras_input.clear()
        self.nombre_input.clear()
        self.cantidad_input.clear()