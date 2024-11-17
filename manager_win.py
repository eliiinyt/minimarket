from PyQt5.QtWidgets import (
    QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QListWidget, QLabel, QTabWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QPainter, QFontMetrics, QPainterPath, QImage
from PyQt5.QtCore import Qt, QRectF, QTimer
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica
from worker_manager import WorkerManager
from styles import get_common_styles
from class_win import ClassWindow


class ManagerWindow(ClassWindow):
    """
    Ventana principal de la aplicación para la gestión de productos.
    Contiene funcionalidades para agregar, modificar y buscar productos,
    organizados en un diseño con pestañas.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.set_window_size_absolute(1440, 900)
        self.setStyleSheet(get_common_styles())

        # Inicialización del manejador de tareas
        self.manager = WorkerManager()

        # Temporizadores para búsquedas
        self.timer_codigo = QTimer(self)
        self.timer_codigo.setInterval(500)
        self.timer_codigo.timeout.connect(self.buscar_por_codigo)

        self.timer_nombre = QTimer(self)
        self.timer_nombre.setInterval(500)
        self.timer_nombre.timeout.connect(self.buscar_por_nombre)

        # Layout principal
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabPosition(QTabWidget.West)

        # Pestaña de gestión de productos
        self.producto_tab = QWidget()
        self.tab_widget.addTab(self.producto_tab, "Gestión de Productos")
        self.producto_layout = QHBoxLayout(self.producto_tab)  # Layout horizontal

        # Pestaña de inicio
        self.home_tab = self.create_home_tab()
        self.tab_widget.addTab(self.home_tab, "Inicio")

        # Configurar la parte izquierda: Formulario de producto
        self.formulario_layout = QVBoxLayout()
        self.setup_formulario()

        # Configurar la parte derecha: Resultados de búsqueda
        self.resultados_layout = QVBoxLayout()
        self.setup_resultados_busqueda()

        # Integrar layouts al layout principal de la pestaña
        self.producto_layout.addLayout(self.formulario_layout, 2)
        self.producto_layout.addLayout(self.resultados_layout, 1)

        # Configurar el layout principal
        self.layout.addWidget(self.tab_widget)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(self.layout)

    def setup_formulario(self):
        """
        Configura el formulario para agregar y modificar productos.
        """
        titulo_formulario = QLabel("Gestión de Productos")
        titulo_formulario.setFont(QFont("Arial", 14, QFont.Bold))

        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')
        self.codigo_barras_input.textChanged.connect(self.iniciar_timer_codigo)

        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText('Nombre del Producto')
        self.nombre_input.textChanged.connect(self.iniciar_timer_nombre)

        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText('Cantidad')

        self.precio_input = QLineEdit(self)
        self.precio_input.setPlaceholderText('Precio')

        self.agregar_button = QPushButton('Agregar Producto', self)
        self.agregar_button.setObjectName('agregar_button')
        self.agregar_button.clicked.connect(self.agregar_producto)

        self.modificar_button = QPushButton('Modificar Producto', self)
        self.modificar_button.setObjectName('modificar_button')
        self.modificar_button.clicked.connect(self.modificar_producto)

        self.formulario_layout.addWidget(titulo_formulario)
        self.formulario_layout.addWidget(self.codigo_barras_input)
        self.formulario_layout.addWidget(self.nombre_input)
        self.formulario_layout.addWidget(self.cantidad_input)
        self.formulario_layout.addWidget(self.precio_input)
        self.formulario_layout.addWidget(self.agregar_button)
        self.formulario_layout.addWidget(self.modificar_button)
        self.formulario_layout.addStretch()  # Agrega espacio extra abajo

    def setup_resultados_busqueda(self):
        """
        Configura el layout de resultados de búsqueda.
        """
        titulo_resultados = QLabel("Resultados de Búsqueda")
        titulo_resultados.setFont(QFont("Arial", 14, QFont.Bold))

        self.resultados_list = QListWidget(self)
        self.resultados_list.itemClicked.connect(self.autocompletar_campos)

        self.resultados_layout.addWidget(titulo_resultados)
        self.resultados_layout.addWidget(self.resultados_list)
        self.resultados_layout.addStretch()  # Espaciado adicional al final

    def iniciar_timer_codigo(self):
        """
        Inicia el temporizador para la búsqueda por código de barras.
        """
        self.timer_codigo.start()

    def iniciar_timer_nombre(self):
        """
        Inicia el temporizador para la búsqueda por nombre.
        """
        self.timer_nombre.start()

    def buscar_por_codigo(self):
        """
        Realiza la búsqueda por código de barras cuando se activa el temporizador.
        """
        self.timer_codigo.stop()
        codigo_barras = self.codigo_barras_input.text().strip()
        if codigo_barras:
            self.resultados_list.clear()
            self.manager.ejecutar_worker(
                func=buscar_producto_logica,
                op_type='buscar_codigo',
                resultado_callback=self.mostrar_resultado_busqueda,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras
            )

    def buscar_por_nombre(self):
        """
        Realiza la búsqueda por nombre cuando se activa el temporizador.
        """
        self.timer_nombre.stop()
        nombre = self.nombre_input.text().strip()
        if nombre:
            self.resultados_list.clear()
            self.manager.ejecutar_worker(
                func=buscar_productos_por_nombre_logica,
                op_type='buscar_nombre',
                resultado_callback=self.mostrar_resultado_busqueda,
                error_callback=self.mostrar_error,
                nombre=nombre
            )

    def agregar_producto_a_lista(self, producto):
        """
        Agrega un producto a la lista de resultados, manejando claves faltantes!
        """
        claves_obligatorias = ['codigo_barras', 'nombre', 'cantidad', 'precio']
        faltantes = [key for key in claves_obligatorias if key not in producto]

        # Construir la representación del producto
        codigo = producto.get('codigo_barras', 'Desconocido')
        nombre = producto.get('nombre', 'Desconocido')
        cantidad = producto.get('cantidad', 'Desconocido')
        precio = producto.get('precio', 'Desconocido')
        self.resultados_list.addItem(f"{codigo} - {nombre} ({cantidad}), {precio}$")

        # Agregar mensajes de claves faltantes
        for key in faltantes:
            self.resultados_list.addItem(f"No se encontró información de '{key}' en el producto '{nombre}'.")

    def mostrar_resultado_busqueda(self, resultados, op_type):
        self.resultados_list.clear()
        if resultados:
            if isinstance(resultados, dict):
                self.agregar_producto_a_lista(resultados)
            elif isinstance(resultados, list):
                for producto in resultados:
                    self.agregar_producto_a_lista(producto)
        else:
            self.resultados_list.addItem("No se encontraron resultados.")


    def autocompletar_campos(self, item):
        """
        Autocompleta los campos del formulario con los datos seleccionados en la lista de resultados.
        """
        try:
            # Parsear datos del texto del elemento seleccionado
            datos = item.text().split(" - ")
            if len(datos) == 2:
                codigo, info = datos
                nombre, detalles = info.split(" (")
                cantidad, precio = detalles[:-1].split("), ")
                print(datos)

                # Asignar valores a los campos del formulario
                self.codigo_barras_input.setText(codigo.strip())
                self.nombre_input.setText(nombre.strip())
                self.cantidad_input.setText(cantidad.strip())
                self.precio_input.setText(precio.replace("$", "").strip())
        except Exception as e:
            self.mostrar_error(f"Error al procesar los datos: {e}", "autocompletar_campos")


    def mostrar_error(self, error, op_type):
        """
        Muestra un mensaje de error en la interfaz.
        """
        self.resultados_list.addItem(f"Error: {error}")


    def create_home_tab(self):
        """
        Crea la pestaña principal con información del usuario.
        """
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

    def agregar_producto(self):
        datos = self.validar_datos_producto()
        if datos:
            codigo_barras, nombre, cantidad, precio = datos
            self.manager.ejecutar_worker(
                func=crear_producto_logica,
                op_type='crear_producto',
                resultado_callback=self.mostrar_mensaje_exito,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras,
                nombre=nombre,
                cantidad=cantidad,
                precio=precio
            )

    def modificar_producto(self):
        datos = self.validar_datos_producto()
        if datos:
            codigo_barras, nombre, cantidad, precio = datos
            self.manager.ejecutar_worker(
                func=modificar_producto_logica,
                op_type='modificar_producto',
                resultado_callback=self.mostrar_mensaje_exito,
                error_callback=self.mostrar_error,
                codigo_barras=codigo_barras,
                nombre=nombre,
                cantidad=cantidad,
                precio=precio
            )

    def mostrar_mensaje_exito(self, resultado, op_type):
        """Muestra un mensaje de éxito."""
        self.resultados_list.addItem("Operación realizada correctamente.")
        self.limpiar_formulario()

    def limpiar_formulario(self):
        """Limpia los campos del formulario."""
        self.codigo_barras_input.clear()
        self.nombre_input.clear()
        self.cantidad_input.clear()
        self.precio_input.clear()

    def validar_datos_producto(self):
        """
        Valida los datos ingresados en el formulario.
        """
        codigo_barras = self.codigo_barras_input.text().strip()
        nombre = self.nombre_input.text().strip()
        try:
            cantidad = int(self.cantidad_input.text().strip())
            precio = float(self.precio_input.text().strip())
            return codigo_barras, nombre, cantidad, precio
        except ValueError:
            self.mostrar_error("Cantidad o precio deben ser valores numéricos.", "validar_datos")
            return None
