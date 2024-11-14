
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
    """