from PyQt5.QtWidgets import (
    QLineEdit, QVBoxLayout, QWidget, QPushButton, QListWidget, QLabel, QHBoxLayout
)
from PyQt5.QtCore import QTimer
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica
from worker_manager import WorkerManager
from styles import get_common_styles
from class_win import ClassWindow


class ManagerWindow(ClassWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.set_window_size_absolute(800, 600)
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

        # Input de código de barras
        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')
        self.codigo_barras_input.setStyleSheet("padding: 10px;")
        self.codigo_barras_input.textChanged.connect(self.iniciar_timer_codigo)

        # Input de nombre
        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText('Nombre del Producto')
        self.nombre_input.setStyleSheet("padding: 10px;")
        self.nombre_input.textChanged.connect(self.iniciar_timer_nombre)

        # Input de cantidad
        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText('Cantidad')
        self.cantidad_input.setStyleSheet("padding: 10px;")

        # Botones
        self.agregar_button = QPushButton('Agregar Producto', self)
        self.agregar_button.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white;")
        self.agregar_button.clicked.connect(self.agregar_producto)

        self.modificar_button = QPushButton('Modificar Producto', self)
        self.modificar_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white;")
        self.modificar_button.clicked.connect(self.modificar_producto)

        # Listas para mostrar resultados
        self.resultados_codigo_label = QLabel("Resultados por Código:")
        self.resultados_codigo_label.setStyleSheet("font-weight: bold;")
        self.resultados_codigo_list = QListWidget(self)

        self.resultados_nombre_label = QLabel("Resultados por Nombre:")
        self.resultados_nombre_label.setStyleSheet("font-weight: bold;")
        self.resultados_nombre_list = QListWidget(self)

        # Agregar elementos al layout
        self.layout.addWidget(self.codigo_barras_input)
        self.layout.addWidget(self.nombre_input)
        self.layout.addWidget(self.cantidad_input)
        self.layout.addWidget(self.agregar_button)
        self.layout.addWidget(self.modificar_button)
        self.layout.addWidget(self.resultados_codigo_label)
        self.layout.addWidget(self.resultados_codigo_list)
        self.layout.addWidget(self.resultados_nombre_label)
        self.layout.addWidget(self.resultados_nombre_list)

        # Configurar el contenedor
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        self.setStyleSheet("background-color: #f0f0f0;")

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
