def validar_username(username: str) -> bool:
    username = username.strip()
    return (len(username) > 0 and len(username) <= 45)

def validar_nombre(nombre: str) -> bool:
    nombre = nombre.strip()
    return (len(nombre) > 0 and len(nombre) <= 100)

def validar_password(password: str) -> bool:
    return len(password) >= 6