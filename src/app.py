from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin

from config import config
from validaciones import *

app = Flask(__name__)

# CORS(app)
CORS(app, resources={r"/*": {"origins": "*"}})

conexion = MySQL(app)


# @cross_origin
# Métodos buenos

#Login
@app.route('/login', methods=['POST'])
def login():
    # Obtiene el username y password del cuerpo de la solicitud
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'mensaje': 'Usuario y contraseña requeridos.', 'exito': False})

    try:
        cursor = conexion.connection.cursor()
        # Consulta para verificar el username y password
        sql = "SELECT nombre FROM usuario WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, password))
        datos = cursor.fetchone()

        if datos:
            return jsonify({'nombre': datos[0], 'mensaje': 'Inicio de sesión exitoso.', 'exito': True})
        else:
            return jsonify({'mensaje': 'Credenciales incorrectas.', 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': 'Error en el servidor.', 'exito': False})

# Registrar usuario
@app.route('/usuarios', methods=['POST'])
def registrar_usuario():
    if (validar_username(request.json['username']) and validar_nombre(request.json['nombre']) and validar_password(request.json['password'])):
        try:
            cursor = conexion.connection.cursor()
            sql = """INSERT INTO usuario (username, password, nombre) 
                     VALUES (%s, %s, %s)"""
            cursor.execute(sql, (request.json['username'], request.json['password'], request.json['nombre']))
            conexion.connection.commit()
            return jsonify({'mensaje': "Usuario registrado.", 'exito': True})
        except Exception as ex:
            return jsonify({'mensaje': "Error", 'exito': False})
    else:
        return jsonify({'mensaje': "Parámetros inválidos...", 'exito': False})

# Obtener preguntas
@app.route('/preguntas', methods=['GET'])
def obtener_preguntas():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT id, descripcion FROM pregunta ORDER BY id ASC"
        cursor.execute(sql)
        datos = cursor.fetchall()
        preguntas = []
        for fila in datos:
            pregunta = {'id': fila[0], 'descripcion': fila[1]}
            preguntas.append(pregunta)
        return jsonify({'preguntas': preguntas, 'mensaje': "Preguntas listadas.", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

# Registrar respuestas de encuesta
@app.route('/respuestas', methods=['POST'])
def registrar_respuestas():
    respuestas = request.json
    
    if not respuestas:
        return jsonify({'mensaje': "No se proporcionaron respuestas.", 'exito': False})
    
    # Validar que todas las respuestas sean numéricas
    if not all(value.isdigit() for value in respuestas.values()):
        return jsonify({'mensaje': "Todas las respuestas deben ser numéricas.", 'exito': False})
    
    try:
        cursor = conexion.connection.cursor()

        # Construir la consulta SQL
        columnas = ', '.join(f'`{key}`' for key in respuestas.keys())
        valores = ', '.join(['%s'] * len(respuestas))
        sql = f"""INSERT INTO respuesta ({columnas}) VALUES ({valores})"""
        
        # Ejecutar la consulta
        cursor.execute(sql, tuple(respuestas.values()))
        conexion.connection.commit()
        
        return jsonify({'mensaje': "Respuestas registradas.", 'exito': True})
    except Exception as ex:
        print(f"Error: {ex}")  # Imprimir error para depuración
        return jsonify({'mensaje': "Error al registrar respuestas.", 'exito': False})


# Obtener respuestas de encuesta
@app.route('/respuestas', methods=['GET'])
def obtener_respuestas():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM respuesta"
        cursor.execute(sql)
        datos = cursor.fetchall()
        respuestas = []
        for fila in datos:
            respuesta = {f"{i + 1}": fila[i + 1] for i in range(len(fila) - 1)}
            respuestas.append(respuesta)
        return jsonify({'respuestas': respuestas, 'mensaje': "Respuestas obtenidas.", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})


# Obtener respuestas de alguno en específico
@app.route('/respuestas/<int:resp_id>', methods=['GET'])
def obtener_respuestas_personales(resp_id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `13`, `14`, `15` FROM respuesta WHERE id = %s"
        cursor.execute(sql, (resp_id,))
        datos = cursor.fetchone()
        if datos:
            respuestas = dict(enumerate(datos, start=1))
            return jsonify({'respuestas': respuestas, 'mensaje': "Respuestas encontradas.", 'exito': True})
        else:
            return jsonify({'mensaje': "No se encontraron respuestas para este usuario.", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

def pagina_no_encontrada(error):
    return "Página no encontrada", 404


if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()