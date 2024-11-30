from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QDialogButtonBox
from PyQt5.QtCore import Qt

class FacturaPopup(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Datos de la Factura")
        self.setModal(True)

        self.total = total


        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Total a pagar: ${total:.2f}"))

        form_layout = QFormLayout()
        self.nombre_input = QLineEdit()
        self.email_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.dinero_recibido_input = QLineEdit()

        form_layout.addRow("Nombre (opcional):", self.nombre_input)
        form_layout.addRow("Correo electrónico (opcional):", self.email_input)
        form_layout.addRow("Teléfono (opcional):", self.telefono_input)
        form_layout.addRow("Dinero recibido:", self.dinero_recibido_input)

        layout.addLayout(form_layout)

        # Botones de Aceptar y Cancelar
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_datos_factura(self):
        """Devuelve los datos capturados en el popup."""
        return {
            "nombre": self.nombre_input.text(),
            "email": self.email_input.text(),
            "telefono": self.telefono_input.text(),
            "dinero_recibido": float(self.dinero_recibido_input.text()) if self.dinero_recibido_input.text() else 0.0
        }
