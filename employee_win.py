from worker import Worker
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QWidget, QPushButton, QTextEdit, QMessageBox
from logic import buscar_producto, registrar_transaccion

class EmployeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Compras")
        self.layout = QVBoxLayout()

        self.transaccion_input = QLineEdit(self)
        self.transaccion_input.setPlaceholderText('Número de Transacción')

        self.volver_login_button = QPushButton('Volver al Login', self)
        self.volver_login_button.clicked.connect(self.volver_al_login)

        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')

        self.agregar_button = QPushButton('Agregar Producto a la Compra', self)
        self.agregar_button.clicked.connect(self.agregar_a_compra)

        self.lista_compras = QTextEdit(self)
        self.lista_compras.setPlaceholderText("Productos en la compra...")

        self.layout.addWidget(self.transaccion_input)
        self.layout.addWidget(self.codigo_barras_input)
        self.layout.addWidget(self.agregar_button)
        self.layout.addWidget(self.lista_compras)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        
        self.productos_seleccionados = []  

    def volver_al_login(self):
        """Vuelve a mostrar la ventana de login."""
        from main import LoginWindow 
        self.login_window = LoginWindow() 
        self.login_window.show() 
        self.close()

    def agregar_a_compra(self):
        """Lógica para agregar productos a una compra en función del código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        transaccion_num = self.transaccion_input.text()

        producto = buscar_producto(codigo_barras)
        if producto:
            self.lista_compras.append(f'Transacción {transaccion_num}: Producto {producto["nombre"]} agregado.')
            self.productos_seleccionados.append({
                'codigo_barras': codigo_barras,
                'nombre': producto['nombre'],
                'cantidad': producto['cantidad']
            })
            self.codigo_barras_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado.")

        if transaccion_num and self.productos_seleccionados:
            if registrar_transaccion(transaccion_num, self.productos_seleccionados):
                QMessageBox.information(self, "Éxito", "Transacción registrada exitosamente.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo registrar la transacción.")