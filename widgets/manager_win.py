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
                      'light': 'stylesheets/test_style.qss'}
        thm = Theme(self)
        json_theme = thm.getTheme()
        thm.applyTheme(json_theme)
        

        # Instancias de la interfaz y el manejador de tareas
        self.ui = ManagerUI(self)
        self.manager = WorkerManager()

        # diseño principal
        self.layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.ui.setup_tabs(self.tab_widget)

        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)
        self.ui.agregar_button.clicked.connect(self.registrar_producto)
        self.ui.modificar_button.clicked.connect(self.registrar_producto)


        # Temporizadores para búsquedas
        self.timer_codigo = QTimer(self)
        self.timer_codigo.setInterval(500)
        self.timer_codigo.timeout.connect(lambda: self.buscar_con_temporizador(self.ui.codigo_barras_input, self.timer_codigo, self.ui.resultados_table, "codigo_barras"))

        self.timer_nombre = QTimer(self)
        self.timer_nombre.setInterval(500)
        self.timer_nombre.timeout.connect(lambda: self.buscar_con_temporizador(self.ui.nombre_input, self.timer_nombre, self.ui.resultados_table, "nombre"))


    
        # Conectar campos de entrada para iniciar los temporizadores
        self.ui.codigo_barras_input.textChanged.connect(self.timer_codigo.start)
        self.ui.nombre_input.textChanged.connect(self.timer_nombre.start)

        self.ui.dark_mode_btn.clicked.connect(lambda: self.changeTheme())


    def changeTheme(self):
            thm = Theme(self)
            if thm.getTheme() == 'dark':
                theme = 'light'
            else:
                theme = 'dark'
            thm.applyTheme(theme)

    def buscar_producto(self, criterio, valor, tabla_destino):
        """
        Busca productos según un criterio (nombre o código de barras) y actualiza la tabla.

        Args:
            criterio (str): El criterio de búsqueda ('nombre' o 'codigo_barras').
            valor (str): El valor a buscar.
            tabla_destino (QTableWidget): La tabla donde se mostrarán los resultados.
        """
        self.manager.ejecutar_worker(
            func=buscar_productos_por_nombre_logica if criterio == "nombre" else buscar_producto_logica,
            op_type=f"buscar_{criterio}",
            resultado_callback=lambda resultados: self.mostrar_resultados_en_tabla(resultados, tabla_destino),
            error_callback=self.ui.mostrar_error,
            **{criterio: valor},  # Pasa el argumento dinámicamente
        )

    def mostrar_resultados_en_tabla(self, resultados, tabla_destino):
        """
        Muestra múltiples productos en una tabla específica.

        Args:
            resultados (list): Lista de diccionarios con información de los productos.
            tabla_destino (QTableWidget): La tabla donde se mostrarán los resultados.
        """
        tabla_destino.setRowCount(0)  # Limpiar la tabla antes de agregar datos

        if resultados: 
            tabla_destino.setRowCount(len(resultados))
            for row, producto in enumerate(resultados):
                # Insertar datos del producto en las filas correspondientes
                tabla_destino.setItem(row, 0, QTableWidgetItem(producto.get("codigo_barras", "N/A")))
                tabla_destino.setItem(row, 1, QTableWidgetItem(producto.get("nombre", "N/A")))
                tabla_destino.setItem(row, 2, QTableWidgetItem(str(producto.get("cantidad", "N/A"))))
                tabla_destino.setItem(row, 3, QTableWidgetItem(f"${producto.get('precio', 0.00):.2f}"))
        else:
            tabla_destino.setRowCount(1)
            tabla_destino.setItem(0, 0, QTableWidgetItem("No se encontraron resultados"))


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


    def buscar_con_temporizador(self, input_field, timer, tabla_destino, criterio):
        """
        Realiza una búsqueda genérica después de un intervalo configurado.

        Args:
            input_field (QLineEdit): Campo de entrada para la búsqueda.
            timer (QTimer): Temporizador asociado a la búsqueda.
            tabla_destino (QTableWidget): Tabla donde se mostrarán los resultados.
            criterio (str): Criterio de búsqueda ('codigo_barras' o 'nombre').
        """
        timer.stop()
        valor = input_field.text().strip()
        if valor:
            self.buscar_producto(criterio=criterio, valor=valor, tabla_destino=tabla_destino)



    def on_tab_changed(self, index):
        """
        Método que se ejecuta cuando se cambia de pestaña.
        """
        current_tab = self.tab_widget.widget(index)

        if current_tab == self.cobro_tab:
            self.setup_cobro_tab_logic()
        else:
            self.stop_all_timers()



    def setup_cobro_tab_logic(self):
        """
        Configura la lógica específica para la pestaña de Cobro.
        """
        if not hasattr(self, "cobro_logic_initialized") or not self.cobro_logic_initialized:
            self.cobro_logic_initialized = True

            # Temporizadores
            self.timer_cobro_codigo = QTimer(self)
            self.timer_cobro_codigo.setInterval(500)
            self.timer_cobro_codigo.timeout.connect(
                lambda: self.buscar_con_temporizador(
                    self.ui.codigo_barras_cobro_input,
                    self.timer_cobro_codigo,
                    self.ui.cobro_search_table,
                    "codigo_barras",
                )
            )

            self.timer_cobro_nombre = QTimer(self)
            self.timer_cobro_nombre.setInterval(500)
            self.timer_cobro_nombre.timeout.connect(
                lambda: self.buscar_con_temporizador(
                    self.ui.nombre_cobro_input,
                    self.timer_cobro_nombre,
                    self.ui.cobro_search_table,
                    "nombre",
                )
            )

            # Conectar eventos
            self.ui.codigo_barras_cobro_input.textChanged.connect(self.timer_cobro_codigo.start)
            self.ui.nombre_cobro_input.textChanged.connect(self.timer_cobro_nombre.start)


    def stop_all_timers(self):
        """
        Detiene todos los temporizadores activos para evitar conflictos.
        """
        for timer in [self.timer_cobro_codigo, self.timer_cobro_nombre]:
            if timer and timer.isActive():
                timer.stop()
