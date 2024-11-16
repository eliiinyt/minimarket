
def get_common_styles():
    return """
    QMainWindow {
        background-color: #f0f0f0;
    }
    
    QLineEdit {
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 14px;
    }
    
    QPushButton {
        padding: 10px;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
    }
    
    QPushButton#agregar_button {
        background-color: #4CAF50;  /* color verde en hex (media hora buscando esto btw) */
    }
    
    QPushButton#modificar_button {
        background-color: #2196F3;  /* color azul en hex */
    }
    
    QListWidget {
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 14px;
    }
    
    QTextEdit {
        padding: 5px;
        border: 1px solid #ccc;
        border-radius: 5px;
        font-size: 14px;
    }

    QTabWidget::tab-bar {
        alignment: left;
    }

    QTabBar::tab {
        height: 100px; /* Aumenta el tamaño de las pestañas */
        width: 50px;
        border: 1px solid #ccc;
        background: #fff;
        margin: 2px;
        padding: 5px;
        text-align: left; /* Alinea el texto a la izquierda */
    }

    QTabBar::tab:selected {
        background: #e0e0e0;
    }

    QTabBar::tab {
        font-size: 12px;
    }

    QWidget {
        border: 1px solid rgba(255, 255, 255, 80);
        border-radius: 15px;
        padding: 15px;
        font-family: Arial, sans-serif;
        font-size: 14px;
        background-color: #f7f7f7;
    }

    QLabel {
        color: #333;
    }

    QLineEdit, QPushButton {
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 8px;
        font-size: 14px;
    }

     QPushButton {
        background-color: #4CAF50;
        color: white;
    }
    
    PushButton:hover {
        background-color: #45a049;
    }
    QPushButton[class='button-login'] {
        padding: 15px 20px;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
        background-color: #4CAF50;
        color: white;
    }
    
    QPushButton[class='button-login']:hover {
        background-color: #45a049;
    }
    
    QPushButton[class='button-register'] {
        padding: 15px 20px;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
        background-color: #2196F3;
        color: white;
    }
    QPushButton[class='button-register']:hover {
        background-color: #1976D2;
    }
    QLabel {
        margin-top: 10px;
    }
"""
