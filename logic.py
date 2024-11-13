
from db import crear_producto, modificar_producto, buscar_producto, buscar_productos_por_nombre
from db import obtener_conexion

def registrar_transaccion(transaccion_num, productos):
    """Registra una transacción en la base de datos."""
    db = obtener_conexion()
    if db is None:
        return False

    try:
        transaccion = {
            'numero_transaccion': transaccion_num,
            'productos': productos
        }
        db['transacciones'].insert_one(transaccion)
        return True
    except Exception as e:
        print(f"Error al registrar la transacción: {e}")
        return False
    

def crear_producto_logica(codigo_barras, nombre, cantidad):
    """Crea un nuevo producto utilizando su código de barras."""
    try:
        return crear_producto(codigo_barras, nombre, cantidad)
    except Exception as e:
        print(f"Error al crear producto: {e}")
        return False

def modificar_producto_logica(codigo_barras, nombre, cantidad):
    """Modifica un producto existente utilizando su código de barras."""
    try:
        return modificar_producto(codigo_barras, nombre, cantidad)
    except Exception as e:
        print(f"Error al modificar producto: {e}")
        return False

def buscar_producto_logica(codigo_barras):
    """Busca un producto por su código de barras."""
    try:
        return buscar_producto(codigo_barras)
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return None

def buscar_productos_por_nombre_logica(nombre):
    """Busca productos por su nombre."""
    try:
        return buscar_productos_por_nombre(nombre)
    except Exception as e:
        print(f"Error al buscar productos: {e}")
        return []