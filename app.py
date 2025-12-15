# app.py

from flask import Flask, jsonify, request, render_template

from flask_cors import CORS 

app = Flask(__name__)
# CORS es crucial para que el frontend (en otro dominio de Render) pueda hablar con este backend.
CORS(app) 

# =========================================================================
# BASES DE DATOS FALSAS (EN MEMORIA)
# =========================================================================

USUARIOS = {
    "admin@motopower.com": "password123",  
    "usuario@test.com": "prueba123",
}

INVENTARIO = [
    {"id": 1, "modelo": "Z900", "marca": "Kawasaki", "cilindraje": "948 cc", "disponibles": 5, "precio": 259900},
    {"id": 2, "modelo": "CB650R", "marca": "Honda", "cilindraje": "649 cc", "disponibles": 3, "precio": 214500},
    {"id": 3, "modelo": "R15 V4", "marca": "Yamaha", "cilindraje": "155 cc", "disponibles": 8, "precio": 105000},
]

MENSAJES = []

# =========================================================================
# ENDPOINTS DE LA API
# =========================================================================

@app.route('/api/register', methods=['POST'])
def register_usuario():
    """Simula el registro de un nuevo usuario con manejo de errores de JSON."""
    
    # PUNTO DE CORRECCIÓN: Intentamos obtener el JSON con manejo de errores
    try:
        datos_registro = request.get_json()
    except Exception:
        # Si la petición no es JSON válido (cuerpo vacío o mal formato)
        return jsonify({"mensaje": "Error en la petición: Asegúrate de que estás enviando JSON válido."}), 400
    
    # Manejar el caso donde get_json() devuelve None (Ej. content-type incorrecto o cuerpo vacío)
    if not datos_registro:
        return jsonify({"mensaje": "Error: El cuerpo de la petición está vacío o no es JSON."}), 400
        
    if 'email' not in datos_registro or 'password' not in datos_registro:
        return jsonify({"mensaje": "Email y contraseña son requeridos para el registro."}), 400
    
    email = datos_registro['email']
    password = datos_registro['password']

    # 1. Verificar si el usuario ya existe
    if email in USUARIOS:
        return jsonify({"mensaje": f"El email {email} ya está registrado."}), 409 

    # 2. Simular el registro 
    USUARIOS[email] = password
    
    # print(f"Nuevo usuario registrado: {email}. Total de usuarios: {len(USUARIOS)}") # Comentado para evitar posibles I/O errors en Render
    return jsonify({
        "mensaje": "Registro exitoso. Ahora puedes iniciar sesión.",
        "usuario": email
    }), 201 

@app.route('/api/login', methods=['POST'])
def login_usuario():
    """Verifica las credenciales del usuario."""
    
    # Implementamos el mismo try/except para el login
    try:
        datos_login = request.get_json()
    except Exception:
        return jsonify({"mensaje": "Error en la petición: El cuerpo de la solicitud no es JSON válido."}), 400
        
    if not datos_login or 'email' not in datos_login or 'password' not in datos_login:
        return jsonify({"mensaje": "Email y contraseña son requeridos"}), 400
    
    email = datos_login['email']
    password = datos_login['password']
    
    if email in USUARIOS and USUARIOS[email] == password:
        # Éxito: Retorna un token simulado
        return jsonify({
            "mensaje": "Inicio de sesión exitoso",
            "token": f"fake_jwt_{email}_hash", 
            "usuario": email
        }), 200
    else:
        # Fallo: Credenciales inválidas
        return jsonify({"mensaje": "Credenciales inválidas. Verifica tu email y contraseña."}), 401

@app.route('/api/inventario', methods=['GET'])
def obtener_inventario():
    """Devuelve la lista completa de motos en el inventario."""
    return jsonify(INVENTARIO)

@app.route('/api/contacto', methods=['POST'])
def recibir_contacto():
    """Recibe los datos del formulario de contacto."""
    
    # Implementamos el mismo try/except para contacto
    try:
        datos_contacto = request.get_json()
    except Exception:
        return jsonify({"mensaje": "Error en la petición: El cuerpo de la solicitud no es JSON válido."}), 400
    
    if not datos_contacto or 'nombre' not in datos_contacto or 'correo' not in datos_contacto or 'mensaje' not in datos_contacto:
        return jsonify({"mensaje": "Datos incompletos"}), 400
    
    MENSAJES.append(datos_contacto)
    
    return jsonify({"mensaje": "¡Gracias! Hemos recibido tu mensaje."}), 201


# =========================================================================
# INICIO DEL SERVIDOR
# =========================================================================

if __name__ == '__main__':
    # Usar host 0.0.0.0 y puerto 5000 para despliegue y pruebas locales
    app.run(host='0.0.0.0', port=5000, debug=True)