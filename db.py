from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bcrypt import hashpw, checkpw, gensalt

def obtener_conexion():
    """Obtiene una conexión a la base de datos MongoDB."""
    try:
        cliente = MongoClient('mongodb+srv://elin:eliiin262144@cluster0.zdkqz.mongodb.net/', serverSelectionTimeoutMS=5000)
        cliente.server_info()  # esto lanzará una excepción si no se conecta y po
        db = cliente['cooperativa']
        return db
    except ConnectionFailure:
        print("Error, no se ha podido conectar con la base de datos.")
        return None

def crear_usuario(email, password, rol):
    """Crea un nuevo usuario en la colección."""
    db = obtener_conexion()
    if db is None:  # verifica si la conexión fue exitosa, supongo.
        return False   # indica que no se pudo conectar, así el usuario no se crea

    coleccion = db['usuarios']
    hashed_password = hashpw(str.encode(password), gensalt())  # Hash de la contraseña
    usuario = {
        'email': email,
        'password': hashed_password.decode(),
        'rol': rol
    }
    coleccion.insert_one(usuario)
    return True 

def autenticar_usuario(email, password):
    """Autentica un usuario."""
    db = obtener_conexion()
    if db is None: 
        return None  

    coleccion = db['usuarios']
    usuario = coleccion.find_one({'email': email})
    if usuario and checkpw(str.encode(password),  str.encode(usuario['password'])):
        return usuario
    return None

def crear_producto(codigo_barras, nombre, cantidad, precio):
    """Crea un nuevo producto en la colección."""
    db = obtener_conexion()
    if db is None:
        return False

    producto = {
        'codigo_barras': codigo_barras,
        'nombre': nombre,
        'cantidad': cantidad,
        'precio': precio
    }
    db['productos'].insert_one(producto)  # Inserta el producto en la colección y que no vuelva a ocurrir
    return True

def modificar_producto(codigo_barras, nombre, cantidad, precio):
    """Modifica un producto existente en la colección."""
    db = obtener_conexion()
    if db is None:
        return False

    resultado = db['productos'].update_one(
        {'codigo_barras': codigo_barras}, 
        {'$set': {'nombre': nombre, 'cantidad': cantidad, 'precio': precio}}
    )
    return resultado.modified_count > 0  # devuelve True si se modificó algo

def buscar_producto(codigo_barras):
    """Busca un producto por su código de barras."""
    db = obtener_conexion()
    if db is None:
        return None

    return db['productos'].find_one({'codigo_barras': codigo_barras})

def buscar_productos_por_nombre(nombre):
    db = obtener_conexion()
    if db is None:
        return []

    try:
        resultados = list(db['productos'].find({'nombre': {'$regex': f".*{nombre}.*", '$options': 'i'}}))
        print(f"Resultados encontrados para '{nombre}': {resultados}")  # Depuración
        return resultados
    except Exception as e:
        print(f"Error al buscar por nombre: {e}")
        return []
    
def crear_factura(datos_factura):
    """
    Crea una nueva factura en la colección 'facturas'.

    :param datos_factura: Diccionario que contiene los datos de la factura.
    :return: True si la factura se creó exitosamente, False en caso contrario.
    """
    db = obtener_conexion()
    if db is None:
        return False

    try:
        db['facturas'].insert_one(datos_factura)  # Inserta la factura en la colección 'facturas'
        return True
    except Exception as e:
        print(f"Error al crear la factura: {e}")
        return False


def obtener_facturas():
    """
    Obtiene todas las facturas desde la colección en la base de datos.
    Devuelve una lista de diccionarios con los campos necesarios para la tabla de historial.
    """
    db = obtener_conexion()
    if db is None:
        return []

    facturas = db['facturas'].find()
    historial = []

    for factura in facturas:
        historial.append({
            "factura_id": factura.get("factura_id", "N/A"),
            "fecha": factura.get("fecha", "Fecha desconocida"),
            "cliente": factura["cliente"],
            "subtotal": factura.get("subtotal", 0.0),
            "efectivo": factura.get("efectivo", 0.0),
            "cambio": factura.get("cambio", 0.0),
        })

    return historial
