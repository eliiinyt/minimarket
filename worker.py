from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    resultado = pyqtSignal(object, str)

    def __init__(self, func, op_type, *args, **kwargs):
        super().__init__()
        self.func = func
        self.op_type = op_type  # Tipo de operación (ej, 'buscar')
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Ejecuta la función en otro hilo."""
        try:
            result = self.func(*self.args, **self.kwargs)  
            self.resultado.emit(result, self.op_type)
        except Exception as e:
            self.resultado.emit(str(e), self.op_type)