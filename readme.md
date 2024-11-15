## Índice
1. [Introducción](#introducción)
2. [Características](#características)
3. [Instalación](#instalación)
4. [Uso](#uso)
5. [Estructura del Proyecto](#estructura-del-proyecto)
6. [Detalles Técnicos](#detalles-técnicos)
7. [Contribuciones](#contribuciones)






## Introducción

Este sistema es una aplicación de escritorio desarrollada en Python utilizando la biblioteca PyQt5. El objetivo principal es gestionar usuarios y productos con funcionalidades como inicio de sesión, registro, búsqueda, creación y modificación de productos. Además, el sistema está conectado a una base de datos MongoDB para almacenar y autenticar la información.

El sistema por ahora permite gestionar productos y usuarios con funcionalidades como:

- Registro e inicio de sesión
- Gestión de productos con una interfaz que por los momentos está apenas con funciones

Como mencioné está construido principalmente con Python, PyQt5 y MongoDB (esto, obviamente sigue WIP y seguramente mientras vaya añadiendo funcionalidades, así mismo iré actualizando el readme)

## Características

En este punto se enumeraran las características que tiene actualmente, esto se irá mejorando mientras se van añadiendo cosas, es simplemente para llevar un roadmap de los avances. Por ahora se cuenta con:
- Autenticación de usuarios con Mongodb que seguramente se cambie a Firebase.
- Gestión de productos: creación, modificación y búsqueda.
- Interfaz visual básica.
- Conexión con base de datos MongoDB.

## Instalación
Por ahora, los requirements están WIP ya que no tengo mucho tiempo para escribir el readme y lo estoy haciendo por partes, así que por lo mientras solo clona el repositorio
   ```bash 
   git clone https://github.com/eliiinyt/minimarket.git
   ```

## uso
Luego de la instalación, simplemente puedes ejecutar con python usando
   ```bash
   python main.py
   ```
Puedes ir variando esto dependiendo de cuál interfaz quieras probar (eso sí, no lo he probado así que seguramente no abran las interfaces porque no se está logueando en el login!)
para loguearte, en caso se que se me haya olvidado hacerles cuenta pueden intentar registrarse y les hará una cuenta de employee para ver la ventana de employee, en caso de que quieran ver la de admin o gerente, pueden loguearse con las credenciales de gerente:

Correo:
```
jggamer12oficial@gmail.com
```
Contraseña:
```
eliiin262144
```

## Detalles Técnicos
Documentación más tecnica.
Tabla de Contenidos

   1. Estructura de Archivos
    2. Descripción Detallada de los Archivos
        auth.py
        db.py
        worker.py
        worker_manager.py
        styles.py
        class_win.py
        manager_win.py
        login_win.py
    3. Flujo de Funcionamiento
    4. Ejemplo de Uso 
    5. Posibles Mejoras


    root/
        ├── auth.py            # Lógica de autenticación
        ├── db.py              # Conexión y operaciones con MongoDB
        ├── worker.py          # Clase Worker para ejecutar tareas en segundo plano
        ├── worker_manager.py  # Gestión de múltiples Workers
        ├── styles.py          # Definición de estilos comunes para la interfaz
        ├── class_win.py       # Clase base para ventanas de PyQt
        ├── manager_win.py     # Ventana de gestión de productos
        ├── login_win.py       # Ventana de inicio de sesión

# Descripción Detallada de los Archivos

# 1. *Auth.py*

Contiene la lógica para la ```autenticación y registro de usuarios```. *Interactúa directamente con db.py* para realizar las operaciones de base de datos.
Sus funciones Principales son:

   * ```iniciar_sesion(email, password)```
      *  Autentica al usuario verificando las credenciales.
      * Retorna el rol del usuario si es válido; de lo contrario, retorna None
    Ejemplo:
    ```
    rol = iniciar_sesion("usuario@test.com", "contraseña123")
if rol:
    print(f"Inicio de sesión exitoso como {rol}")
else:
    print("Credenciales incorrectas")
    ```

* ```registrar_usuario(email, password, rol="empleado")```
* Crea un nuevo usuario en la base de datos.
* Ejemplo:
```
if registrar_usuario("nuevo@test.com", "contraseña456"):
    print("Usuario registrado exitosamente")
else:
    print("Error en el registro")
```    



# 2. *db.py*

*Funciones Principales*:

  * obtener_conexion()
        Retorna una conexión activa a la base de datos. Si falla, retorna None.

  * crear_usuario(email, password, rol)
        Inserta un nuevo usuario en la base de datos.

  * autenticar_usuario(email, password)
        Busca al usuario y verifica la contraseña con un hash seguro.



# 3. *worker.py*

Este define la clase ```Worker```, que es una implementación personalizada de hilos en PyQt para manejar tareas en segundo plano.
*Clase:* ```Worker```

* *Propiedades:*
    * ```func```: Función a ejecutar.
    * ```args y kwargs```: Argumentos de la función.
    * Señales para comunicar el resultado o errores.

* Metodos claves:
    * ```__init__```: Recibe una función (```func```) que será ejecutada en el worker, el tipo de operación (```op_type```), y cualquier argumento adicional que la función pueda necesitar.
    * ```run```:Este es el método que se ejecuta cuando el worker comienza su tarea en el hilo. Llama a la función (```func```) con los argumentos proporcionados y emite el ```resultado``` a través de la señal resultado. Si ocurre un error, emite una señal ```error```.

* Código:
``` 

from PyQt5.QtCore import QThread, pyqtSignal

class Worker(QThread):
    resultado = pyqtSignal(object, str)  # Emitirá el resultado y el tipo de operación
    error = pyqtSignal(str, str)        # Emitirá el error y el tipo de operación

    def __init__(self, func, op_type, *args, **kwargs):
        super().__init__()
        self.func = func
        self.op_type = op_type  # Tipo de operación (por ejemplo, 'buscar')
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Ejecuta la función asignada en un hilo separado."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.resultado.emit(result, self.op_type)
        except Exception as e:
            self.error.emit(str(e), self.op_type)
```
Cuando se crea una instancia del ```Worker```, se le pasa una función que se ejecutará en un hilo separado.
Cuando la función termina su ejecución, emite una señal con el resultado. Si ocurre un error, también emite una señal de error.


* *uso:*
```
worker = Worker(func=my_function, args=(arg1, arg2))
worker.resultado.connect(handle_result)
worker.error.connect(handle_error)
worker.start()
```

# 4. *worker_manager.py*

El WorkerManager es una clase que gestiona múltiples instancias de ```Worker```. La principal responsabilidad del ```WorkerManager``` es ejecutar tareas en segundo plano (en hilos separados) y mantener un registro de los workers activos, permitiendo así ejecutar varias tareas en segundo plano.

* Componentes principales del ```WorkerManager```:

    1. Lista de workers (```self.workers```):
        Mantiene un seguimiento de los workers que están activos y que aún no han terminado.

    2. Método ```ejecutar_worker```:
        * Crea un nuevo ```Worker``` y lo inicia. Este método también conecta las señales ```resultado``` y ```error``` a las funciones callback correspondientes.
        * Además, conecta la señal ```finished``` para eliminar el worker de la lista de workers activos una vez que termine.

    3. Método _limpiar_worker:
        * Cuando un worker termina su tarea, este método lo elimina de la lista de workers activos.

* *Uso del* ```WorkerManager```: Cuando desees ejecutar una tarea en segundo plano (por ejemplo, realizar una consulta a la base de datos sin bloquear la interfaz gráfica), puedes usar el WorkerManager de la siguiente manera:
    1. Crea un *callback* que maneje el resultado de la tarea.
    2. Pasa el *callback de resultado* y el *callback de error* (si es necesario) al llamar ```ejecutar_worker``` del ```WorkerManager```.
    * Ejemplo:
    ```
    def buscar_producto(self):
        codigo_barras = self.codigo_input.text()
        self.manager.ejecutar_worker(
            func=buscar_producto_en_db,
            op_type='buscar_producto',
            resultado_callback=self.mostrar_resultado,
            error_callback=self.mostrar_error,
            codigo_barras=codigo_barras
        )
    ```
        
    * En este ejemplo, ```buscar_producto_en_db``` es la función que se ejecutará en un hilo separado, y las funciones ```mostrar_resultado``` y ```mostrar_error``` serán llamadas cuando el worker termine con éxito o falle.

* Clase: ```WorkerManager```
    * *Métodos:*
        * ```ejecutar_worker(func, op_type, resultado_callback, error_callback, **kwargs)```
        * Ejecuta un ```Worker``` con una función y sus parámetros.
        * Conecta las señales de resultado y error a los callbacks proporcionados.
    






- **Hilos:** Implementados con `Worker` y gestionados por `WorkerManager`.






- **Base de datos:** Conexión con MongoDB usando `pymongo`.




- **Estilos:** Uniformizados en `styles.py` para consistencia visual.


## Contribuciones
¡Las contribuciones son bienvenidas! Por favor, abre un *pull request* o reporta problemas en la sección de *issues*.

