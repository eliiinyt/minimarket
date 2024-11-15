from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget, QLabel, QPushButton, QProgressBar
from PyQt5.QtCore import Qt
from worker_manager import WorkerManager
from styles import get_common_styles
from class_win import ClassWindow
from auth import iniciar_sesion, registrar_usuario

class LoginWindow(ClassWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Inicio de Sesión')
        self.set_window_size_absolute(800, 600)
        self.setStyleSheet(get_common_styles())

        self.manager = WorkerManager()  # Manejo de hilos con WorkerManager

        # Layout principal
        self.layout = QVBoxLayout()

        # Título
        self.titulo_label = QLabel("Inicio de Sesión", self)
        self.titulo_label.setAlignment(Qt.AlignCenter)
        self.titulo_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")

        # Campo de email
        self.email_input = QLineEdit(self)
        self.email_input.setPlaceholderText('Email')
        self.email_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")

        # Campo de contraseña
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Contraseña')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")

        # Botón de inicio de sesión
        self.login_button = QPushButton('Iniciar Sesión', self)
        self.login_button.setStyleSheet("padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.login_button.clicked.connect(self.iniciar_sesion)

        # Botón de registro
        self.register_button = QPushButton('Registrar', self)
        self.register_button.setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border-radius: 5px;")
        self.register_button.clicked.connect(self.registrar_usuario)

        # Etiqueta de mensaje
        self.mensaje_label = QLabel(self)
        self.mensaje_label.setAlignment(Qt.AlignCenter)
        self.mensaje_label.setStyleSheet("color: red; margin-top: 10px;")

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)

        # Añadir widgets al layout
        self.layout.addWidget(self.titulo_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.mensaje_label)

        # Contenedor central
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        self.setStyleSheet("background-color: #f5f5f5;")

    def iniciar_sesion(self):
        """Inicia el proceso de inicio de sesión en segundo plano."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.mostrar_mensaje("Por favor, rellena todos los campos.", "red")
            return

        # Mostrar barra de progreso y deshabilitar botones
        self.progress_bar.setVisible(True)
        self.login_button.setEnabled(False)
        self.register_button.setEnabled(False)

        # Ejecutar el login en un Worker
        self.manager.ejecutar_worker(
            func=iniciar_sesion,
            op_type='login',
            resultado_callback=self.handle_login_result,
            error_callback=self.handle_login_error,
            email=email,
            password=password
        )

    def handle_login_result(self, rol, op_type):
        """Maneja el resultado del login."""
        self.progress_bar.setVisible(False)
        self.login_button.setEnabled(True)
        self.register_button.setEnabled(True)

        if rol:
            self.mostrar_mensaje(f"¡Bienvenido {rol}!", "green")
            self.ventana_principal(rol)
        else:
            self.mostrar_mensaje("Email o contraseña incorrectos.", "red")

    def handle_login_error(self, error, op_type):
        """Maneja errores en el proceso de login."""
        self.progress_bar.setVisible(False)
        self.login_button.setEnabled(True)
        self.register_button.setEnabled(True)
        self.mostrar_mensaje(f"Error: {error}", "red")

    def registrar_usuario(self):
        """Registra un nuevo usuario."""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            self.mostrar_mensaje("Por favor, rellena todos los campos.", "red")
            return

        try:
            registrar_usuario(email, password)
            self.mostrar_mensaje("Usuario registrado exitosamente.", "green")
        except Exception as e:
            self.mostrar_mensaje(f"Error al registrar: {e}", "red")

    def mostrar_mensaje(self, mensaje, color):
        """Muestra un mensaje en la etiqueta."""
        self.mensaje_label.setText(mensaje)
        self.mensaje_label.setStyleSheet(f"color: {color};")

    def ventana_principal(self, rol):
        """Abre la ventana principal según el rol del usuario."""
        from manager_win import ManagerWindow
        from employee_win import EmployeeWindow

        if rol == "empleado":
            self.main_window = EmployeeWindow()
        else:
            self.main_window = ManagerWindow()
        self.main_window.show()
        self.close()
