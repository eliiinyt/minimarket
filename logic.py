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
    

def crear_producto_logica(codigo_barras, nombre, cantidad, precio):
    """Crea un nuevo producto utilizando su código de barras."""
    try:
        return crear_producto(codigo_barras, nombre, cantidad, precio)
    except Exception as e:
        print(f"Error al crear producto: {e}")
        return False

def modificar_producto_logica(codigo_barras, nombre, cantidad, precio):
    """Modifica un producto existente utilizando su código de barras."""
    try:
        return modificar_producto(codigo_barras, nombre, cantidad, precio)
    except Exception as e:
        print(f"Error al modificar producto: {e}")
        return False

def buscar_producto_logica(codigo_barras):
    try:
        producto = buscar_producto(codigo_barras)
        if producto:
            print(producto)
            return [{"codigo_barras": producto["codigo_barras"], "nombre": producto["nombre"],
                     "cantidad": producto["cantidad"], "precio": producto["precio"]}]
        return []
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return []


def buscar_productos_por_nombre_logica(nombre):
    """Busca productos por su nombre."""
    try:
        producto = buscar_productos_por_nombre(nombre)
        if producto:
            return [{"codigo_barras": producto["codigo_barras"], "nombre": producto["nombre"],
                     "cantidad": producto["cantidad"], "precio": producto["precio"]}]
        return []
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return []