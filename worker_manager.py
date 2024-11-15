from worker import Worker

class WorkerManager:
    def __init__(self):
        self.workers = []

    def ejecutar_worker(self, func, op_type, resultado_callback, error_callback=None, *args, **kwargs):
        """Crea y ejecuta un nuevo Worker"""
        worker = Worker(func, op_type, *args, **kwargs)
        worker.resultado.connect(resultado_callback)
        if error_callback:
            worker.error.connect(error_callback)
        worker.finished.connect(lambda: self._limpiar_worker(worker))
        self.workers.append(worker)
        worker.start()

    def _limpiar_worker(self, worker):
        """Elimina el worker terminado de la lista"""
        if worker in self.workers:
            self.workers.remove(worker)
