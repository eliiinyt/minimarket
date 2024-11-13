from db import crear_usuario, autenticar_usuario

def iniciar_sesion(email, password):
    """Inicia sesión y retorna el rol del usuario si es exitoso."""
    usuario = autenticar_usuario(email, password)
    if usuario:
        return usuario['rol'] # debería terminar cosas luego pero meh
    return None

def registrar_usuario(email, password, rol="empleado"):
    """Registra un nuevo usuario con un rol predeterminado."""
    crear_usuario(email, password, rol)