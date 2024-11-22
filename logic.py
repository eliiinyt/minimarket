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

def buscar_productos_por_nombre_logica(nombre):
    """Busca productos por nombre utilizando MongoDB."""
    try:
        productos = buscar_productos_por_nombre(nombre)  # Debería devolver una lista de documentos
        if productos:
            return [
                {
                    "codigo_barras": producto.get("codigo_barras", "N/A"),
                    "nombre": producto.get("nombre", "N/A"),
                    "cantidad": producto.get("cantidad", 0),
                    "precio": producto.get("precio", 0.0)
                }
                for producto in productos
            ]
        return []
    except Exception as e:
        print(f"Error al buscar productos por nombre: {e}")
        return []


def buscar_producto_logica(codigo_barras):
    """Busca un producto por su código de barras utilizando MongoDB."""
    try:
        producto = buscar_producto(codigo_barras)  # Debería devolver un documento único
        if producto:
            return [
                {
                    "codigo_barras": producto.get("codigo_barras", "N/A"),
                    "nombre": producto.get("nombre", "N/A"),
                    "cantidad": producto.get("cantidad", 0),
                    "precio": producto.get("precio", 0.0)
                }
            ]
        return []
    except Exception as e:
        print(f"Error al buscar producto por código de barras: {e}")
        return []
