import json

from PyQt5.QtCore import QFile, QTextStream
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit


class Theme:
    def __init__(self, parent):
        self.widget = parent

    def getTheme(self):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            return settings.get('theme', 'light')  # Retorna 'light' por defecto si no se encuentra nada

    def applyTheme(self, theme_key):
        """
        @type theme_key: str
        """
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            settings = {}
        settings['theme'] = theme_key

        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)

        # Aplicar el tema al widget

        self.widget.style().unpolish(self.widget)
        file = QFile(self.widget.theme[theme_key])
        if not file.open(QFile.ReadOnly | QFile.Text):
            raise Exception("FileNotFound")
        style = QTextStream(file)
        self.widget.setStyleSheet(style.readAll())
        self.widget.style().polish(self.widget)
        self.widget.update()


 # mejoré esto, solo muestra un mensaje en la pantalla!
def show_message(self, title, message, msg_type="info"):
    """Popup para mostrar mensajes"""
    if msg_type == "info":
        QMessageBox.information(self, title, message)
    elif msg_type == "warning":
        QMessageBox.warning(self, title, message)
    elif msg_type == "error":
        QMessageBox.critical(self, title, message)



# shows message with a QLineEdit to enter a text
def showDialog(widget, title, message):
    text, ok = QInputDialog.getText(widget, title, message, QLineEdit.Normal)
    if ok:
        return text
    return None


# shows a yes or no question
def askQuestion(widget, title, message):
    buttonReply = QMessageBox.question(widget, title, message, QMessageBox.Yes or QMessageBox.No, QMessageBox.No)
    if buttonReply == QMessageBox.Yes:
        return True
    return False