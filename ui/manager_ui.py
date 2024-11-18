from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QWidget, QTabWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QFont


class ManagerUI:
    def __init__(self, parent):
        self.parent = parent

    def setup_tabs(self, tab_widget):
        """
        Configura las pestañas principales.
        """
        # Pestaña de gestión de productos
        self.producto_tab = QWidget()
        self.setup_producto_tab(self.producto_tab)
        tab_widget.addTab(self.producto_tab, "Gestión de Productos")

        # Pestaña de inicio
        self.home_tab = QWidget()
        self.setup_home_tab(self.home_tab)
        tab_widget.addTab(self.home_tab, "Inicio")

    def setup_producto_tab(self, tab):
        """
        Configura la pestaña de gestión de productos.
        """
        layout = QHBoxLayout(tab)

        # Formulario (izquierda)
        self.formulario_layout = QVBoxLayout()
        self.setup_formulario(self.formulario_layout)
        layout.addLayout(self.formulario_layout, 2)

        # Resultados (derecha)
        self.resultados_layout = QVBoxLayout()
        self.setup_resultados(self.resultados_layout)
        layout.addLayout(self.resultados_layout, 2)

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

    def setup_home_tab(self, tab):
        """
        Configura la pestaña de inicio.
        """
        layout = QVBoxLayout(tab)

        titulo = QLabel("Bienvenido al Gestor de Productos")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(titulo)


    def mostrar_error(self, error):
        """
        Muestra un error en la lista de resultados.
        """
        self.resultados_list.addItem(f"Error: {error}")


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



