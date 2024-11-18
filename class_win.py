from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QVBoxLayout
from PyQt5.QtGui import QGuiApplication
import qtmodern.windows

class ClassWindow(QMainWindow):
    def __init__(self): 
        """
        Clase base para todas las ventanas.
        :param apply_modern_style: Si es True, aplica el estilo moderno automáticamente.
        """
        super().__init__()
        self.setStyleSheet("stylesheets/login-light.qss")  # Estilo básico por defecto

    def show_message(self, title, message, msg_type="info"):
        """Popup para mostrar mensajes"""
        if msg_type == "info":
            QMessageBox.information(self, title, message)
        elif msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)

    def limpiar_formulario(self):
        """Método para limpiar formularios en subclases."""
        pass

    def set_window_title(self, title):
        """Establece el título de la ventana."""
        self.setWindowTitle(title)

    def set_window_size_absolute(self, width_px, height_px):
        """Establece el tamaño de la ventana basado en resolución de pantalla."""
        screen = QGuiApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        anchoVentana = (screen_size.width() * width_px) / 1920
        altoVentana = (screen_size.height() * height_px) / 1080
        
        self.setFixedSize(int(anchoVentana), int(altoVentana))
