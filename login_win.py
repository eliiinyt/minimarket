from worker import Worker 
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from auth import registrar_usuario, iniciar_sesion
from styles import get_common_styles
from class_win import ClassWindow
class LoginWindow(ClassWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Inicio de Sesión')
        self.set_window_size_absolute(800, 600)
        self.setStyleSheet(get_common_styles())
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
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            self.show_message("Error", "Por favor, rellena todos los campos.", "warning")
            return
        
        rol = iniciar_sesion(email, password)
        if rol:
            self.show_message("Éxito", f'Bienvenido {rol}!')
            self.ventana_principal(rol)
        else:
            self.show_message("Error", "Email o contraseña incorrectos.", "warning")

    def registrar_usuario(self):
        """Registro de nuevos usuarios"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            self.show_message("Error", "Por favor, rellena todos los campos.", "warning")
            return
            
        rol = "empleado"
        if registrar_usuario(email, password, rol):
            self.show_message("Registro", "Usuario registrado exitosamente.")
        else:
            self.show_message("Error", "Error al registrar el usuario.", "error")

    def ventana_principal(self, rol):
        """Ventana principal según el rol del usuario"""
        from manager_win import ManagerWindow
        from employee_win import EmployeeWindow
        
        if rol == "empleado":
            self.main_window = EmployeeWindow()
        else:
            self.main_window = ManagerWindow()
        self.main_window.show()
        self.close()