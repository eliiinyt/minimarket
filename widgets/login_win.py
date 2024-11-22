from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from backend.auth import iniciar_sesion, registrar_usuario
from backend.worker_manager import WorkerManager
from widgets.ui_functions import Theme, showMessage
from ui.login_ui import LoginUI
from PyQt5.QtCore import Qt

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.setWindowTitle('Inicio de Sesión')
        self.setWindowIcon(QIcon('res/images/icon-128px.png'))
        self.setFixedSize(400, 500)
        self.theme = {'dark': 'stylesheets/login-dark.qss',
                      'light': 'stylesheets/login-light.qss'}
        thm = Theme(self)
        json_theme = thm.getTheme()
        thm.applyTheme(json_theme)

        self.ui = LoginUI()
        self.setCentralWidget(self.ui)

        self.ui.login_button.clicked.connect(self.iniciar_sesion)
        self.ui.register_button.clicked.connect(self.registrar_usuario)
        self.ui.password_input.returnPressed.connect(self.iniciar_sesion)
        self.manager = WorkerManager()

    def iniciar_sesion(self):
        email = self.ui.email_input.text().strip()
        password = self.ui.password_input.text().strip()

        if not email or not password:
            showMessage(self.ui.mensaje_label, "Por favor, rellena todos los campos.", "red")
            return
        self.ui.progress_bar.setVisible(True)
        self.ui.login_button.setEnabled(False)
        self.ui.register_button.setEnabled(False)

        self.manager.ejecutar_worker(
            func=iniciar_sesion,
            op_type="login",
            resultado_callback=self.handle_login_result,
            error_callback=self.handle_login_error,
            email=email,
            password=password
        )

    def handle_login_result(self, rol, op_type):
        """Maneja el resultado del login."""
        self.ui.progress_bar.setVisible(False)
        self.ui.login_button.setEnabled(True)
        self.ui.register_button.setEnabled(True)

        if rol:
            #showMessage(self.ui.mensaje_label, f"¡Bienvenido {rol}!", "green")
            self.ventana_principal(rol)
        else:
           showMessage(self.ui.mensaje_label,"Email o contraseña incorrectos.", "red")

    def handle_login_error(self, error, op_type):
        """Maneja errores en el proceso de login."""
        self.ui.progress_bar.setVisible(False)
        self.ui.login_button.setEnabled(True)
        self.ui.register_button.setEnabled(True)
        showMessage(self.ui.mensaje_label, f"Error: {error}", "red")

    def registrar_usuario(self):
        email = self.ui.email_input.text().strip()
        password = self.ui.password_input.text().strip()
        try:
            registrar_usuario(email, password)
            showMessage(self.ui.mensaje_label, "Usuario registrado exitosamente.", "green")
        except Exception as e:
            showMessage(self.ui.mensaje_label, f"Error al registrar: {e}", "red")

    def ventana_principal(self, rol):
        """Abre la ventana principal según el rol del usuario."""
        from widgets.manager_win import ManagerWindow
        from widgets.employee_win import EmployeeWindow

        if rol == "empleado":
            self.main_window = EmployeeWindow()
        else:
            self.main_window = ManagerWindow()
        
        self.main_window.show()  # Muestra la nueva ventana
        self.close()  # Cierra la ventana actual

