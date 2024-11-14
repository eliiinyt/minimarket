from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget, QPushButton, QMessageBox, QListWidget
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica
from worker import Worker
from styles import get_common_styles
from class_win import ClassWindow
class ManagerWindow(ClassWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.set_window_size_absolute(800, 600)
        self.setStyleSheet(get_common_styles())

        self.layout = QVBoxLayout()
        
        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')
        self.codigo_barras_input.setStyleSheet("padding: 10px;")
        self.codigo_barras_input.textChanged.connect(self.iniciar_busqueda_codigo)

        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText('Nombre del Producto')
        self.nombre_input.setStyleSheet("padding: 10px;")
        self.nombre_input.textChanged.connect(self.iniciar_busqueda_nombre) 

        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText('Cantidad')
        self.cantidad_input.setStyleSheet("padding: 10px;")

        self.agregar_button = QPushButton('Agregar Producto', self)
        self.agregar_button.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white;")
        self.agregar_button.clicked.connect(self.agregar_producto)

        self.modificar_button = QPushButton('Modificar Producto', self)
        self.modificar_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white;")
        self.modificar_button.clicked.connect(self.modificar_producto)

        self.producto_list = QListWidget(self) 
        self.layout.addWidget(self.codigo_barras_input)
        self.layout.addWidget(self.nombre_input)
        self.layout.addWidget(self.cantidad_input)
        self.layout.addWidget(self.agregar_button)
        self.layout.addWidget(self.modificar_button)
        self.layout.addWidget(self.producto_list)  

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.setStyleSheet("background-color: #f0f0f0;")
        
        self.workers = []

    def iniciar_busqueda_codigo(self):
        """Inicia un hilo para buscar el producto en la base de datos por código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        if codigo_barras:  # POR FAVOR SOLO INICIA SI HAY TEXTO Y NO ME MATES EL PC OTRA VEZ
            worker = Worker(buscar_producto_logica, 'buscar_codigo')
            worker.args = (codigo_barras,)
            worker.resultado.connect(self.handle_busqueda_codigo)
            self.workers.append(worker)
            worker.start()

    def iniciar_busqueda_nombre(self):
        """Inicia un hilo para buscar productos en la base de datos por nombre."""
        nombre = self.nombre_input.text()
        if nombre:
            worker = Worker(buscar_productos_por_nombre_logica, 'buscar_nombre')
            worker.args = (nombre,)
            worker.resultado.connect(self.handle_busqueda_nombre)
            self.workers.append(worker)
            worker.start()

    def handle_busqueda_codigo(self, producto, op_type):
        if producto:
            self.nombre_input.setText(producto['nombre'])
            self.cantidad_input.setText(str(producto['cantidad']))
        else:
            self.nombre_input.clear()
            self.cantidad_input.clear()

    def handle_busqueda_nombre(self, productos, op_type):
        self.producto_list.clear()
        if productos:
            for producto in productos:
                self.producto_list.addItem(f"{producto['codigo_barras']} - {producto['nombre']}")
        else:
            self.producto_list.addItem("No se encontraron productos.")

    def agregar_producto(self):
        """Lógica para agregar productos usando el código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        nombre = self.nombre_input.text()
        try:
            cantidad = int(self.cantidad_input.text())
            if crear_producto_logica(codigo_barras, nombre, cantidad):
                QMessageBox.information(self, "Éxito", f'Producto {nombre} agregado con código {codigo_barras}!')
                self.limpiar_formulario()
            else:
                QMessageBox.warning(self, "Error", "No se pudo conectar a la base de datos.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese una cantidad válida.")

    def modificar_producto(self):
        """Lógica para modificar productos usando el código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        nombre = self.nombre_input.text()
        try:
            cantidad = int(self.cantidad_input.text())
            if modificar_producto_logica(codigo_barras, nombre, cantidad):
                QMessageBox.information(self, "Éxito", f'Producto {nombre} modificado con código {codigo_barras}!')
                self.limpiar_formulario()
            else:
                QMessageBox.warning(self, "Error", "No se pudo conectar a la base de datos.")
        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor ingrese una cantidad válida.")

    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.codigo_barras_input.clear()
        self.nombre_input.clear()
        self.cantidad_input.clear()