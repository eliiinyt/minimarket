# esto es inutil e inmantenible, ya modifiqué todo para dejarlo en archivos independientes
from PyQt5.QtWidgets import (QMainWindow, QLineEdit, QVBoxLayout, 
                             QWidget, QLabel, QPushButton, QMessageBox, QTextEdit)
from logic import crear_producto, modificar_producto, buscar_producto, registrar_transaccion
from auth import registrar_usuario, iniciar_sesion

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Inicio de Sesión')
        self.layout = QVBoxLayout()

        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Contraseña')
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Iniciar Sesión', self)
        self.login_button.clicked.connect(self.iniciar_sesion)

        self.register_button = QPushButton('Registrar', self)
        self.register_button.clicked.connect(self.registrar_usuario)

        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def iniciar_sesion(self):
        """Manejo de inicio de sesión."""
        email = self.email_input.text()
        password = self.password_input.text()
        rol = iniciar_sesion(email, password)
        if rol:
            QMessageBox.information(self, "Éxito", f'Bienvenido {rol}!')
            self.ventana_principal(rol)
        else:
            if rol is None:
                QMessageBox.warning(self, "Error", "Error, no se ha podido conectar con la base de datos.")
            else:
                QMessageBox.warning(self, "Error", "Email o contraseña incorrectos.")

    def registrar_usuario(self):
        """Maneja el registro de nuevos usuarios."""
        email = self.email_input.text()
        password = self.password_input.text()
        rol = "empleado"
        if registrar_usuario(email, password, rol):
            QMessageBox.information(self, "Registro", "Usuario registrado exitosamente.")
        else:
            QMessageBox.warning(self, "Error", "Error al registrar el usuario.")

    def ventana_principal(self, rol):
        """Muestra la ventana principal según el rol del usuario."""
        if rol == "empleado":
            self.main_window = EmployeeWindow()
        else:
            self.main_window = ManagerWindow()
        self.main_window.show()
        self.close()


class ManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Productos")
        self.layout = QVBoxLayout()

        self.codigo_barras_input = QLineEdit(self)
        self.codigo_barras_input.setPlaceholderText('Código de Barras')

        self.nombre_input = QLineEdit(self)
        self.nombre_input.setPlaceholderText('Nombre del Producto')

        self.cantidad_input = QLineEdit(self)
        self.cantidad_input.setPlaceholderText('Cantidad')

        self.agregar_button = QPushButton('Agregar Producto', self)
        self.agregar_button.clicked.connect(self.agregar_producto)

        self.modificar_button = QPushButton('Modificar Producto', self)
        self.modificar_button.clicked.connect(self.modificar_producto)

        self.layout.addWidget(self.codigo_barras_input)
        self.layout.addWidget(self.nombre_input)
        self.layout.addWidget(self.cantidad_input)
        self.layout.addWidget(self.agregar_button)
        self.layout.addWidget(self.modificar_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def agregar_producto(self):
        """Lógica para agregar productos usando el código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        nombre = self.nombre_input.text()
        try:
            cantidad = int(self.cantidad_input.text())
            if crear_producto(codigo_barras, nombre, cantidad):
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
            if modificar_producto(codigo_barras, nombre, cantidad):
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


class EmployeeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Compras")
        self.layout = QVBoxLayout()

        self.transaccion_input = QLineEdit(self)
        self.transaccion_input.setPlaceholderText('Número de Transacción')

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

    def agregar_a_compra(self):
        """Lógica para agregar productos a una compra en función del código de barras."""
        codigo_barras = self.codigo_barras_input.text()
        transaccion_num = self.transaccion_input.text()

        producto = buscar_producto(codigo_barras)
        if producto:
            self.lista_compras.append(f'Transacción {transaccion_num}: Producto {producto["nombre"]} agregado.')
            self.codigo_barras_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Producto no encontrado.")