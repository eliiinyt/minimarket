from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QMessageBox
from backend.worker_manager import WorkerManager
from ui.manager_ui import ManagerUI
import os 
from datetime import datetime
import uuid
from widgets.popup import FacturaPopup
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode.code128 import Code128
from widgets.ui_functions import Theme, show_message
from functools import partial
import json
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget
from PyQt5.QtCore import QTimer
from logic import crear_producto_logica, modificar_producto_logica, buscar_producto_logica, buscar_productos_por_nombre_logica
from db import crear_factura, obtener_facturas

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
        

        # Instancias de la interfaz y worker
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
        self.ui.agregar_a_cesta_button.clicked.connect(self.agregar_a_cesta)
        self.ui.productos_table.cellDoubleClicked.connect(self.seleccionar_producto_desde_tabla)
        self.ui.pagar_button.clicked.connect(self.mostrar_popup_factura)
        self.cargar_historial()
        self.ui.reload_button.clicked.connect(self.cargar_historial)



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
                "tabla": self.ui.productos_table,
                "timer": self.timer_busqueda
            },
            self.ui.codigo_barras_cobro_input: {
                "criterio": "codigo_barras",
                "tabla": self.ui.productos_table,
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
                    error_callback=lambda: show_message(self, "modificar_producto_logica", "error", "warning"),
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
                    self.ui.productos_table,
                    "codigo_barras",
                )
            )

            self.timer_cobro_nombre = QTimer(self)
            self.timer_cobro_nombre.setInterval(500)
            self.timer_cobro_nombre.timeout.connect(
                lambda: self.buscar_con_temporizador(
                    self.ui.nombre_cobro_input,
                    self.timer_cobro_nombre,
                    self.ui.productos_table,
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


    def mostrar_popup_factura(self):
            # Total de la cesta
            total = self.calcular_total_cesta()

            # Mostrar el popup
            popup = FacturaPopup(total, self)
            if popup.exec_():  # Si se confirma el diálogo
                datos_cliente = popup.get_datos_factura()

                # Validar dinero recibido, cambio y por ultimo generrar la factura
                dinero_recibido = datos_cliente["dinero_recibido"]
                if dinero_recibido < total:
                    QMessageBox.warning(self, "Error", "El dinero recibido es insuficiente.")
                    return
                cambio = dinero_recibido - total

                self.generar_factura(datos_cliente, total, cambio)



    def generar_factura(self, datos_cliente, total, cambio):
        """Genera una factura en PDF utilizando los datos del cliente y la cesta."""
        productos = self.obtener_datos_cesta()
        settings = cargar_settings()
        factura_id = str(uuid.uuid4()) # esto luego lo cambio a cocmo dijo Ruva

        datos_factura = {
            "factura_id": factura_id,
            "fecha": datetime.now().isoformat(),
            "direccion": settings.get("direccion", "Dirección no configurada"),
            "telefono": settings.get("telefono", "Teléfono no configurado"),
            "cajero": "#2",  # esto luego tengo que implementarlo
            "gerente": settings.get("gerente", "Gerente no configurado"),
            "productos": productos,
            "subtotal": total,
            "efectivo": datos_cliente["dinero_recibido"],
            "cambio": cambio,
            "cliente": {
                "nombre": datos_cliente.get("nombre", "Cliente Anónimo"),
                "email": datos_cliente.get("email", ""),
                "telefono": datos_cliente.get("telefono", "")
            }
        }

        # Crear la factura en PDF con el workeruwu
        self.manager.ejecutar_worker(
            func=lambda: crear_factura(datos_factura), 
            op_type=f"creando factura",
            resultado_callback= self.factura_guardada_exitosamente,
            error_callback=lambda: show_message(self, "crear_factura", "error", "warning")
        )
        print("Productos:", productos)
        self.crear_factura_pdf(f"factura_{factura_id}.pdf", datos_factura)

        # Mensaje de confirmación
        QMessageBox.information(self, "Factura Generada", "La factura ha sido generada con éxito.")

    def calcular_total_cesta(self):
        """Calcula el total de los productos en la cesta."""
        total = 0.0
        for row in range(self.ui.cobro_search_table.rowCount()):
            subtotal = float(self.ui.cobro_search_table.item(row, 3).text().strip('$'))
            total += subtotal
        return total
    
    def obtener_datos_cesta(self):
        """Obtiene los datos de los productos en la cesta."""
        productos = []
        for row in range(self.ui.cobro_search_table.rowCount()):
            codigo_barras = self.ui.cobro_search_table.item(row, 0).text()  # Si tienes este dato
            nombre = self.ui.cobro_search_table.item(row, 1).text()
            cantidad = int(self.ui.cobro_search_table.item(row, 2).text())
            precio = float(self.ui.cobro_search_table.item(row, 3).text().strip('$'))
            subtotal = cantidad * precio
            productos.append({
                "codigo_barras": codigo_barras,
                "nombre": nombre,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal
            })
        return productos

        # self.crear_factura_pdf(nombre_archivo, datos_factura)

        # Llamar a la función para imprimir
        # self.imprimir_factura(nombre_archivo)




    def crear_factura_pdf(self, nombre_archivo, datos_factura):
        c = canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # Encabezado
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2.0, height - 50, "SUPERMARKET")

        # Datos del cliente
        c.setFont("Helvetica", 12)
        cliente = datos_factura["cliente"]
        c.drawString(30, height - 80, f"Nombre: {cliente['nombre']}")
        c.drawString(30, height - 100, f"Email: {cliente['email']}")
        c.drawString(30, height - 120, f"Teléfono: {cliente['telefono']}")


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
        #y -= 80
        #c.drawString(30, y, "codigo de barras:")
        #barcode = Code128(datos_factura["codigo_barras"], barHeight=40, barWidth=1.2)
        #barcode.drawOn(c, 30, y - 50)

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
            print(f"Error al imprimir: {e}")

    def agregar_a_cesta(self, codigo, nombre, cantidad, precio):
        """
        Añade un producto a la cesta y actualiza la tabla y el total.
        """
        cantidad_text = cantidad.strip()

        if not cantidad_text.isdigit():
            QMessageBox.warning(self, "Error", "Por favor, introduce una cantidad válida.")
            return

        cantidad = int(cantidad_text)
        if cantidad <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0.")
            return

        # Calcular subtotal!
        subtotal = precio * cantidad

        # Agregar a la tabla de la cesta, me duele todo ayuda
        row_position = self.ui.cobro_search_table.rowCount()
        self.ui.cobro_search_table.insertRow(row_position)
        self.ui.cobro_search_table.setItem(row_position, 0, QTableWidgetItem(codigo))
        self.ui.cobro_search_table.setItem(row_position, 1, QTableWidgetItem(nombre))
        self.ui.cobro_search_table.setItem(row_position, 2, QTableWidgetItem(str(cantidad)))
        self.ui.cobro_search_table.setItem(row_position, 3, QTableWidgetItem(f"${precio:.2f}"))
        self.ui.cobro_search_table.setItem(row_position, 4, QTableWidgetItem(f"${subtotal:.2f}"))

        # Actualizar el total
        total_actual = float(self.ui.total_label.text().split('$')[1])
        total_actual += subtotal
        self.ui.total_label.setText(f"Total: ${total_actual:.2f}")

        # Limpiar campos
        self.ui.codigo_barras_cobro_input.clear()
        self.ui.nombre_cobro_input.clear()
        #self.ui.cantidad_cobro_input.clear()
        self.ui.codigo_barras_cobro_input.setFocus()  # Focalizar en el campo de código de barras para el siguiente producto

    def seleccionar_producto_desde_tabla(self, row, column):
        """
        Obtiene los datos del producto seleccionado desde la tabla
        y los pasa a la función de agregar a la cesta.
        """
        tabla = self.ui.productos_table

        # Validar que la fila seleccionada está dentro del rango de filas válidas
        if row >= tabla.rowCount() or row < 0:
            print(f"Error: La fila {row} está fuera del rango válido.")
            return

        # Validar que la celda no sea None, importante!!!!!
        item_codigo = tabla.item(row, 0)  # Columna Código
        item_nombre = tabla.item(row, 1)  # Columna Nombre
        item_cantidad = tabla.item(row, 2)  # Columna Cantidad
        item_precio = tabla.item(row, 3)  # Columna Precio

        if not (item_codigo and item_nombre and item_precio):
            print(f"Error: Una o más celdas están vacías en la fila {row}.")
            return

        try:
            # Extraer valores de las celdas
            codigo = item_codigo.text()
            nombre = item_nombre.text()
            cantidad = item_cantidad.text()
            precio = float(item_precio.text().strip('$'))  # Convertir precio a float
        except Exception as e:
            print(f"Error al procesar los datos de la fila {row}: {e}")
            return

        # Llamar a la función para agregar a la cesta
        self.agregar_a_cesta(codigo, nombre, cantidad, precio)

    def factura_guardada_exitosamente(self, resultado):
        """Callback que se ejecuta cuando la factura se guarda correctamente."""
        if resultado:
            print(self, "Éxito", "La factura se guardó en la base de datos exitosamente.")
        else:
            QMessageBox.warning(self, "Error", "Ocurrió un problema al guardar la factura en la base de datos.")



    def cargar_historial(self):
        """
        Carga los datos de la base de datos en la tabla de historial usando un worker.
        """
        self.ui.historial_table.setRowCount(0) 
        self.ui.status_label.setText("Cargando historial...")

        self.manager.ejecutar_worker(
            func=obtener_facturas,  
            op_type="cargar_historial", 
            resultado_callback=self._rellenar_tabla_historial,
            error_callback=self.ui.mostrar_error 
        )

    def _rellenar_tabla_historial(self, facturas):
        """
        Rellena la tabla de historial con los datos obtenidos del worker.
        """
        if not facturas:
            self.ui.status_label.setText("No hay facturas disponibles en el historial.")
            return

        for factura in facturas:
            row_position = self.ui.historial_table.rowCount()
            self.ui.historial_table.insertRow(row_position)
            if isinstance(factura["cliente"], dict):
                cliente_nombre = factura["cliente"].get("nombre", "Cliente Desconocido")
            else:
                print(f"Error: Cliente no es un diccionario. Es de tipo {type(factura['cliente'])}: {factura['cliente']}")
                cliente_nombre = "Dato Inválido"

            # Rellenar columnas como pavo en navidad
            self.ui.historial_table.setItem(row_position, 0, QTableWidgetItem(str(factura["factura_id"])))
            self.ui.historial_table.setItem(row_position, 1, QTableWidgetItem(factura["fecha"]))
            self.ui.historial_table.setItem(row_position, 2, QTableWidgetItem(cliente_nombre))
            self.ui.historial_table.setItem(row_position, 3, QTableWidgetItem(f"${factura['subtotal']:.2f}"))
            self.ui.historial_table.setItem(row_position, 4, QTableWidgetItem(f"${factura['efectivo']:.2f}"))
            self.ui.historial_table.setItem(row_position, 5, QTableWidgetItem(f"${factura['cambio']:.2f}"))

        self.ui.status_label.setText(f"Se cargaron {len(facturas)} facturas en el historial.")




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
    

