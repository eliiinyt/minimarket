from worker import Worker 
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
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
        from manager_win import ManagerWindow
        from employee_win import EmployeeWindow
        
        if rol == "empleado":
            self.main_window = EmployeeWindow()
        else:
            self.main_window = ManagerWindow()
        self.main_window.show()
        self.close()