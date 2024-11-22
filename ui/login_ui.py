from PyQt5.QtWidgets import (
    QLineEdit, QVBoxLayout, QLabel, QPushButton, QProgressBar, QWidget, 
    QHBoxLayout, QSpacerItem, QSizePolicy, QCheckBox, 
)
from PyQt5.QtCore import Qt

class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.titulo_label = QLabel("🍁 Inicio de Sesión 🍁", self)
        self.titulo_label.setObjectName("TituloLabel")
        self.email_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.login_button = QPushButton('Iniciar Sesión', self)
        self.register_button = QPushButton('Registrar', self)
        self.mensaje_label = QLabel(self)

        self.email_label = QLabel("Correo electrónico", self)
        self.password_label = QLabel("Contraseña", self)

        # Checkbox para mostrar contraseña
        self.show_password_checkbox = QCheckBox("Mostrar contraseña", self)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)

        # Enlace para recuperar contraseña
        self.forgot_password_button = QPushButton("¿Olvidaste tu contraseña?", self)
        self.forgot_password_button.setObjectName("forgot_password_button")
        self.forgot_password_button.setFlat(True)

        # Barra de progreso
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)

        self._setup_ui()

    def _setup_ui(self):
        self.titulo_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.progress_bar.setVisible(False)

        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Espaciador superior
        self.layout.addWidget(self.titulo_label)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.show_password_checkbox)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)
        self.layout.addWidget(self.forgot_password_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.mensaje_label)

        link_layout = QHBoxLayout()
        link_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addWidget(self.forgot_password_button, alignment=Qt.AlignCenter)
        link_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout.addLayout(link_layout)

        self.setLayout(self.layout)

    def toggle_password_visibility(self, state):
        """Alterna la visibilidad del texto de la contraseña."""
        if state == Qt.Checked:
            self.password_input.setEchoMode(QLineEdit.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
