import sys
from PyQt5.QtWidgets import QApplication
from login_win import LoginWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = LoginWindow()
    ventana.show() # si le dices está bonito pero en tu mente no piensas eso
    sys.exit(app.exec_())