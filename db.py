from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from werkzeug.security import generate_password_hash, check_password_hash

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
    hashed_password = generate_password_hash(password)  # Hash de la contraseña
    usuario = {
        'email': email,
        'password': hashed_password,
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
    if usuario and check_password_hash(usuario['password'], password):
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
    """Busca productos por su nombre (puede ser parcial)."""
    db = obtener_conexion()
    if db is None:
        return []

    # regex mis huevos lkJHLKASHDKLASJHD
    return list(db['productos'].find({'nombre': {'$regex': nombre, '$options': 'i'}}))  #