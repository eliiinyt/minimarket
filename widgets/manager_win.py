from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from backend.worker_manager import WorkerManager
from ui.manager_ui import ManagerUI

from widgets.ui_functions import Theme, showMessage

from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget
from PyQt5.QtCore import QTimer
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica

class ManagerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.resize(1440, 900)
        self.theme = {'dark': 'stylesheets/dark.qss',
                      'light': 'stylesheets/light.qss'}
        thm = Theme(self)
        json_theme = thm.getTheme()
        thm.applyTheme(json_theme)

        # Instancias de la interfaz y el manejador de tareas
        self.ui = ManagerUI(self)
        self.manager = WorkerManager()

        # Configurar el diseño principal
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.ui.setup_tabs(self.tab_widget)

        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
        self.ui.agregar_button.clicked.connect(self.registrar_producto)
        self.ui.modificar_button.clicked.connect(self.registrar_producto)


        # Temporizadores para búsquedas
        self.timer_codigo = QTimer(self)
        self.timer_codigo.setInterval(500)
        self.timer_codigo.timeout.connect(self.buscar_por_codigo)
      
        self.timer_nombre = QTimer(self)
        self.timer_nombre.setInterval(500)
        self.timer_nombre.timeout.connect(self.buscar_por_nombre)

        self.ui.codigo_barras_input.textChanged.connect(self.timer_codigo.start)
        self.ui.nombre_input.textChanged.connect(self.timer_nombre.start)


    def buscar_por_codigo(self):
        """
        Busca un producto por código de barras usando un temporizador y actualiza la tabla.
        """
        self.timer_codigo.stop()
        codigo = self.ui.codigo_barras_input.text().strip()
        if codigo:
            self.manager.ejecutar_worker(
                func=buscar_producto_logica,
                op_type="buscar_codigo",
                resultado_callback=self.mostrar_resultado_en_tabla,
                error_callback=self.ui.mostrar_error,
                codigo_barras=codigo,
            )

    def buscar_por_nombre(self):
        """
        Busca productos por nombre usando un temporizador y actualiza la tabla.
        """
        self.timer_nombre.stop()
        nombre = self.ui.nombre_input.text().strip()
        if nombre:
            self.manager.ejecutar_worker(
                func=buscar_productos_por_nombre_logica,
                op_type="buscar_nombre",
                resultado_callback=self.mostrar_resultados_en_tabla,
                error_callback=self.ui.mostrar_error,
                nombre=nombre,
            )
    def mostrar_resultado_en_tabla(self, resultado):
        """
        Muestra un único producto en la tabla de resultados. Maneja el caso de listas.
        """
        self.ui.resultados_table.setRowCount(0)

        # Si el resultado es una lista, toma el primer elemento
        if isinstance(resultado, list) and len(resultado) > 0:
            resultado = resultado[0]

        if isinstance(resultado, dict):
            self.ui.resultados_table.setRowCount(1)
            self.ui.resultados_table.setItem(0, 0, QTableWidgetItem(resultado.get("codigo_barras", "N/A")))
            self.ui.resultados_table.setItem(0, 1, QTableWidgetItem(resultado.get("nombre", "N/A")))
            self.ui.resultados_table.setItem(0, 2, QTableWidgetItem(str(resultado.get("cantidad", "N/A"))))
            self.ui.resultados_table.setItem(0, 3, QTableWidgetItem(f"${resultado.get('precio', 0.00):.2f}"))
        else:
            self.ui.resultados_table.setRowCount(1)
            self.ui.resultados_table.setItem(0, 0, QTableWidgetItem("No se encontró el producto"))

    def mostrar_resultados_en_tabla(self, resultados):
        """
        Muestra múltiples productos en la tabla de resultados.
        """
        self.ui.resultados_table.setRowCount(0)
        if resultados:
            self.ui.resultados_table.setRowCount(len(resultados))
            for row, producto in enumerate(resultados):
                self.ui.resultados_table.setItem(row, 0, QTableWidgetItem(producto["codigo_barras"]))
                self.ui.resultados_table.setItem(row, 1, QTableWidgetItem(producto["nombre"]))
                self.ui.resultados_table.setItem(row, 2, QTableWidgetItem(str(producto["cantidad"])))
                self.ui.resultados_table.setItem(row, 3, QTableWidgetItem(f"${producto['precio']:.2f}"))
        else:
            self.ui.resultados_table.setRowCount(1)
            self.ui.resultados_table.setItem(0, 0, QTableWidgetItem("No se encontraron resultados"))


    def registrar_producto(self):
        """
        Registra un producto en la base de datos utilizando los datos ingresados en el formulario.
        """
        codigo_barras = self.ui.codigo_barras_input.text().strip()
        nombre = self.ui.nombre_input.text().strip()
        cantidad = self.ui.cantidad_input.text().strip()
        precio = self.ui.precio_input.text().strip()

        if not (codigo_barras and nombre and cantidad and precio):
            self.ui.mostrar_error("Todos los campos son obligatorios.")
            return

        try:
            cantidad = int(cantidad)
            precio = float(precio)
        except ValueError:
            self.ui.mostrar_error("La cantidad debe ser un número entero y el precio un valor decimal.")
            return

        resultado = crear_producto_logica(codigo_barras, nombre, cantidad, precio)
        if resultado:
            self.ui.mostrar_resultados([{"codigo_barras": codigo_barras, "nombre": nombre, "cantidad": cantidad, "precio": precio}])
        else:
            self.ui.mostrar_error("Error al registrar el producto.")


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


