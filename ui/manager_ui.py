from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QToolButton, QLabel, QPushButton, QLineEdit, QListWidget, QWidget, QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont, QPixmap, QImage, QPainterPath, QPainter, QIcon
from PyQt5.QtCore import Qt, QRectF, QSize

class ManagerUI:
    def __init__(self, parent):
        self.parent = parent
        self.tab_widget = None
        self.hidden_tabs = {}  # Almacena las pestañas ocultas por su nombre

        self.tabs = {
            "Inicio": self.setup_home_tab,
            "Gestión de Productos": self.setup_producto_tab,
            "Configuración": self.setup_configuration,
            "Cobro": self.setup_cobro_tab,
            "Historial": lambda tab: self.generic_tab(tab, "Contenido del Historial"),
        }

    def setup_tabs(self, tab_widget):
        """
        Configura las pestañas principales con un menú lateral.
        """
        layout = QHBoxLayout()
        tab_widget.setContentsMargins(0, 0, 0, 0)

        # Menú lateral
        side_menu = QVBoxLayout()
        self.setup_side_menu(side_menu)
        side_menu_widget = QWidget()
        side_menu_widget.setLayout(side_menu)
        side_menu_widget.setFixedWidth(200)
        layout.addWidget(side_menu_widget)

        # Contenido principal (pestañas)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.hide_tab)
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.setup_content_tabs()
        layout.addWidget(self.tab_widget, 1)

        tab_widget.setLayout(layout)
        

    def setup_side_menu(self, layout):
        """
        Configura el menú lateral de navegación.
        """
        logo = QLabel("Gestor")
        logo.setFont(QFont("Arial", 20, QFont.Bold))
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        buttons = [
            ("Inicio", "res/icons/home.png"),
            ("Gestión de Productos", "res/icons/productos.png"),
            ("Configuración", "res/icons/configuracion.png"),
            ("Cobro", "res/icons/ventas.png"),
            ("Historial", "res/icons/historial.png"),
        ]

        for text, icon_path in buttons:
            button = QToolButton()
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(24, 24))
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            button.setText(text)
            button.setStyleSheet("padding: 5px;")
            button.clicked.connect(lambda _, t=text: self.show_or_open_tab(t))
            layout.addWidget(button)

        layout.addStretch()

    


### TABS

    def setup_cobro_tab(self, tab):
        """
        Configura la pestaña de cobro de productos.
        """
        layout = QVBoxLayout(tab)

        # Título de la pestaña
        titulo = QLabel("Cobro de Productos")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titulo)

        # Formulario para agregar productos a la cesta
        form_layout = QHBoxLayout()

        self.codigo_barras_cobro_input = QLineEdit()
        self.codigo_barras_cobro_input.setPlaceholderText("Código de Barras")
        form_layout.addWidget(self.codigo_barras_cobro_input)

        self.nombre_cobro_input = QLineEdit()
        self.nombre_cobro_input.setPlaceholderText("nombre")
        form_layout.addWidget(self.nombre_cobro_input)

        self.agregar_cesta_button = QPushButton("Agregar a la Cesta")
        #self.agregar_cesta_button.clicked.connect(self.agregar_a_cesta)
        form_layout.addWidget(self.agregar_cesta_button)

        layout.addLayout(form_layout)

        # Tabla para mostrar los productos en la cesta
        self.cobro_search_table = QTableWidget()
        self.cobro_search_table.setColumnCount(4)
        self.cobro_search_table.setHorizontalHeaderLabels(["Código", "Nombre", "Cantidad", "Precio"])
        self.cobro_search_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Solo lectura
        layout.addWidget(self.cobro_search_table)

        # Total y opciones de pago
        total_layout = QHBoxLayout()
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setFont(QFont("Arial", 16, QFont.Bold))
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()

        self.pagar_button = QPushButton("Pagar")
        #self.pagar_button.clicked.connect(self.procesar_pago)
        total_layout.addWidget(self.pagar_button)

        layout.addLayout(total_layout)
        tab.setLayout(layout)

    def setup_home_tab(self, tab):
        """
        Configura la pestaña de inicio.
        """
        layout = QVBoxLayout(tab)

        titulo = QLabel("Bienvenido al Gestor de Productos")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titulo)


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
        self.light_mode_btn = QPushButton("Modo Claro")
        self.dark_mode_btn = QPushButton("Modo Oscuro")
        restart_btn = QPushButton("Reiniciar Explorador")
        quick_settings_layout.addWidget(self.light_mode_btn)
        quick_settings_layout.addWidget(self.dark_mode_btn)
        quick_settings_layout.addWidget(restart_btn)
        layout.addLayout(quick_settings_layout)
        tab.setLayout(layout)

    def setup_producto_tab(self, tab):
        """
        Configura la pestaña de gestión de productos.
        """
        layout = QVBoxLayout(tab)

        formulario_layout = QVBoxLayout()
        self.setup_formulario(formulario_layout)
        layout.addLayout(formulario_layout)

        resultados_layout = QVBoxLayout()
        self.setup_resultados(resultados_layout)
        layout.addLayout(resultados_layout)

    def setup_formulario(self, layout):
        """
        Configura el formulario de la pestaña de productos.
        """
        titulo = QLabel("Gestión de Productos")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))

        self.codigo_barras_input = QLineEdit()
        self.codigo_barras_input.setPlaceholderText("Código de Barras")

        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre del Producto")

        self.cantidad_input = QLineEdit()
        self.cantidad_input.setPlaceholderText("Cantidad")

        self.precio_input = QLineEdit()
        self.precio_input.setPlaceholderText("Precio")

        self.agregar_button = QPushButton("Agregar Producto")
        self.modificar_button = QPushButton("Modificar Producto")

        layout.addWidget(titulo)
        layout.addWidget(self.codigo_barras_input)
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.cantidad_input)
        layout.addWidget(self.precio_input)
        layout.addWidget(self.agregar_button)
        layout.addWidget(self.modificar_button)

    def setup_resultados(self, layout):
        """
        Configura la sección de resultados con una tabla.
        """
        titulo = QLabel("Resultados de Búsqueda")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))

        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(4)
        self.resultados_table.setHorizontalHeaderLabels(["Código", "Nombre", "Cantidad", "Precio"])
        self.resultados_table.setEditTriggers(QTableWidget.NoEditTriggers)  # Solo lectura

        layout.addWidget(titulo)
        layout.addWidget(self.resultados_table)

    def setup_content_tabs(self):
        """
        Configura las pestañas iniciales.
        """
        self.home_tab = QWidget()
        self.setup_home_tab(self.home_tab)
        self.tab_widget.addTab(self.home_tab, "Inicio")

        self.producto_tab = QWidget()
        self.setup_producto_tab(self.producto_tab)
        self.tab_widget.addTab(self.producto_tab, "Gestión de Productos")

        self.cobro_tab = QWidget()
        self.setup_cobro_tab(self.cobro_tab)
        self.tab_widget.addTab(self.cobro_tab, "Cobro")
    
    def setup_configuration(self, tab):
        """
        Configura la pestaña de configuración.
        """
        layout = QVBoxLayout(tab)

        titulo = QLabel("Bienvenido a la configuración!")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titulo)

        # Sección de configuraciones rápidas
        quick_settings_layout = QVBoxLayout()
        quick_settings_label = QLabel("Configuraciones Rápidas")
        quick_settings_label.setFont(QFont("Arial", 14, QFont.Bold))
        quick_settings_layout.addWidget(quick_settings_label)
        self.light_mode_btn = QPushButton("Modo Claro")
        self.dark_mode_btn = QPushButton("Modo Oscuro")
        restart_btn = QPushButton("Reiniciar Explorador")
        quick_settings_layout.addWidget(self.light_mode_btn)
        quick_settings_layout.addWidget(self.dark_mode_btn)
        quick_settings_layout.addWidget(restart_btn)
        layout.addLayout(quick_settings_layout)
        tab.setLayout(layout)

    
### Funcionalidades

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

    def mostrar_error(self, error):
        """
        Muestra un error en la lista de resultados.
        """
        self.resultados_list.addItem(f"Error: {error}")

    def mostrar_resultados(self, resultados):
        self.resultados_table.setRowCount(0)
        if not resultados:
            self.resultados_table.setRowCount(1)
            self.resultados_table.setItem(0, 0, QTableWidgetItem("Sin resultados"))
            return
        self.resultados_table.setRowCount(len(resultados))
        for row, producto in enumerate(resultados):
            self.resultados_table.setItem(row, 0, QTableWidgetItem(producto.get("codigo_barras", "")))
            self.resultados_table.setItem(row, 1, QTableWidgetItem(producto.get("nombre", "")))
            self.resultados_table.setItem(row, 2, QTableWidgetItem(str(producto.get("cantidad", ""))))
            self.resultados_table.setItem(row, 3, QTableWidgetItem(f"${producto.get('precio', 0):.2f}"))


    def show_or_open_tab(self, tab_name):
        """
        Muestra una pestaña oculta o abre una nueva si no existe.
        """
        # Si la pestaña está oculta, vuelve a mostrarla
        if tab_name in self.hidden_tabs:
            tab, index = self.hidden_tabs.pop(tab_name)
            self.tab_widget.insertTab(index, tab, tab_name)
            self.tab_widget.setCurrentWidget(tab)
            return

        # Si la pestaña ya existe, actívala
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_name:
                self.tab_widget.setCurrentIndex(i)
                return

        # Si no existe, crea una nueva
        new_tab = QWidget()
        if tab_name in self.tabs:
            self.tabs[tab_name](new_tab)
        self.tab_widget.addTab(new_tab, tab_name)
        self.tab_widget.setCurrentWidget(new_tab)

    def hide_tab(self, index):
        """
        Oculta una pestaña!
        """
        tab_name = self.tab_widget.tabText(index)
        tab = self.tab_widget.widget(index)
        self.hidden_tabs[tab_name] = (tab, index)
        self.tab_widget.removeTab(index)


    def generic_tab(self, tab, content_text):
        """
        Configura una pestaña genérica con contenido textual.
        """
        layout = QVBoxLayout(tab)
        label = QLabel(content_text)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        tab.setLayout(layout)
