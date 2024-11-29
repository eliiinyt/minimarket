from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from backend.worker_manager import WorkerManager
from ui.manager_ui import ManagerUI
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.code128 import Code128
from widgets.ui_functions import Theme, showMessage
from functools import partial
import json
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


        # Temporizadr dde busqueda
        self.timer_busqueda = QTimer(self)
        self.timer_busqueda.setInterval(500)
        self.timer_busqueda.timeout.connect(self.realizar_busqueda)

        # mapeo lal
        self.campos_busqueda = {
            self.ui.codigo_barras_input: {
                "criterio": "codigo_barras",
                "tabla": self.ui.resultados_table,
                "timer": self.timer_busqueda
            },
            self.ui.nombre_input: {
                "criterio": "nombre",
                "tabla": self.ui.resultados_table,
                "timer": self.timer_busqueda
            },
            self.ui.nombre_cobro_input: {
                "criterio": "nombre",
                "tabla": self.ui.cobro_search_table,
                "timer": self.timer_busqueda
            },
            self.ui.codigo_barras_cobro_input: {
                "criterio": "codigo_barras",
                "tabla": self.ui.cobro_search_table,
                "timer": self.timer_busqueda
            }
        }


        self.campo_actual = None

        def conectar_campo(campo):
            campo.textChanged.connect(lambda: self.set_campo_actual(campo))
            campo.textChanged.connect(self.timer_busqueda.start)

        for input_field in self.campos_busqueda.keys():
            conectar_campo(input_field)


        self.ui.dark_mode_btn.clicked.connect(lambda: self.changeTheme())
        self.ui.light_mode_btn.clicked.connect(lambda: self.generar_factura())



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


    def stop_all_timers(self):
        """
        Detiene todos los temporizadores activos para evitar conflictos.
        """
        for timer in [self.timer_cobro_codigo, self.timer_cobro_nombre]:
            if timer and timer.isActive():
                timer.stop()


    def realizar_busqueda(self):
        print("realizar_busqueda ha sido llamada")
        if not self.campo_actual:
            print("No hay un campo actual seleccionado")
            return

        config_campo = self.campos_busqueda.get(self.campo_actual)
        if not config_campo:
            print(f"No hay configuración para el campo {self.campo_actual}")
            return
        print(config_campo)
        config_campo["timer"].stop()
        texto = self.campo_actual.text().strip()
        print(texto)
        criterio = config_campo["criterio"]
        tabla = config_campo["tabla"]

        print(f"Buscando por criterio: {criterio}, texto: {texto}")
        if texto:
            self.buscar_producto(criterio=criterio, valor=texto, tabla_destino=tabla)
        else:
            print("Texto vacío, no se realiza búsqueda.")

    def set_campo_actual(self, campo):
        """Establece el campo actual activo y arranca el temporizador."""
        print(f"Campo actual cambiado a: {campo.objectName()}")
        self.campo_actual = campo
        self.timer_busqueda.start()





    def generar_factura(self):
        settings = cargar_settings()
        datos_factura = {
            "direccion": settings.get("direccion", "Dirección no configurada"),
            "telefono": settings.get("telefono", "Teléfono no configurado"),
            "cajero": "#2",
            "gerente": settings.get("gerente", "Gerente no configurado"),
            "productos": [
                {"nombre": "dildo", "cantidad": 1, "precio": 9.20},
                {"nombre": "A520M-k", "cantidad": 1, "precio": 19.20},
                {"nombre": "Vaselina", "cantidad": 1, "precio": 15.00},
            ],
            "subtotal": 43.70,
            "efectivo": 200.00,
            "cambio": 156.60,
            "codigo_barras": "123456789012"
        }
        nombre_archivo = "factura_supermercado.pdf"
        self.crear_factura_pdf(nombre_archivo, datos_factura)

        # Llamar a la función para imprimir
        # self.imprimir_factura(nombre_archivo)




    def crear_factura_pdf(self, nombre_archivo, datos_factura):
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 50, "SUPERMARKET")

        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2.0, height - 70, datos_factura["direccion"])
        c.drawCentredString(width / 2.0, height - 90, f"Tel.: {datos_factura['telefono']}")

        # Cajero y gerente
        c.drawString(30, height - 130, f"Cajero: {datos_factura['cajero']}")
        c.drawString(200, height - 130, f"Gerente: {datos_factura['gerente']}")

        # Línea separadora
        c.setStrokeColor(colors.black)
        c.line(30, height - 140, width - 30, height - 140)

        # Tabla de productos
        c.setFont("Helvetica-Bold", 10)
        c.drawString(30, height - 160, "Nombre")
        c.drawString(200, height - 160, "Cantidad")
        c.drawString(250, height - 160, "Precio")

        y = height - 180
        for producto in datos_factura["productos"]:
            c.setFont("Helvetica", 10)
            c.drawString(30, y, producto["nombre"])
            c.drawString(200, y, str(producto["cantidad"]))
            c.drawString(250, y, f"${producto['precio']:.2f}")
            y -= 20

        # Subtotal, efectivo y cambio
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, y - 20, f"Sub Total: ${datos_factura['subtotal']:.2f}")
        c.drawString(30, y - 40, f"Efectivo: ${datos_factura['efectivo']:.2f}")
        c.drawString(30, y - 60, f"Cambio: ${datos_factura['cambio']:.2f}")

        # Código de barras
        y -= 80
        c.drawString(30, y, "codigo de barras:")
        barcode = Code128(datos_factura["codigo_barras"], barHeight=40, barWidth=1.2)
        barcode.drawOn(c, 30, y - 50)

        # Mensaje final
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2.0, y - 120, "¡Gracias por su compra!")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2.0, y - 140, "Esperamos verte de vuelta!")

        c.save()


    def imprimir_factura(self, archivo_pdf):
        """
        Imprime un archivo PDF usando el comando `lp` en sistemas compatibles (Linux/macOS).
        En Windows, utiliza el comando `print`.
        """
        try:
            if os.name == "posix":  # Linux/marcOS
                os.system(f"lp {archivo_pdf}")
            elif os.name == "nt":  # güinDOS
                os.startfile(archivo_pdf, "print")
        except Exception as e:
            print(f"Error al imprimir: {e}")


def cargar_settings(ruta="settings.json"):
    if os.path.exists(ruta):
        with open(ruta, "r") as archivo:
            try:
                return json.load(archivo)
            except json.JSONDecodeError:
                print("Error al leer el archivo settings.json")
                return {}
    else:
        print(f"No se encontró el archivo {ruta}")
        return {}