from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QLabel, QPushButton, QProgressBar, QWidget

class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.titulo_label = QLabel("Inicio de Sesión", self)
        self.email_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.login_button = QPushButton('Iniciar Sesión', self)
        self.register_button = QPushButton('Registrar', self)
        self.mensaje_label = QLabel(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)

        self._setup_ui()

    def _setup_ui(self):
        self.titulo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.progress_bar.setVisible(False)

        self.layout.addWidget(self.titulo_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.mensaje_label)
        self.setLayout(self.layout)
