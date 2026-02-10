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

    "admin@motopower.com": {
        "password": "password123",
        "role": "admin",
        "carrito": []
    }
}

    



INVENTARIO = [
    {"id": 1, "modelo": "Z900", "marca": "Kawasaki", "cilindraje": "948 cc", "disponibles": 5, "precio": 259900},
    {"id": 2, "modelo": "CB650R", "marca": "Honda", "cilindraje": "649 cc", "disponibles": 3, "precio": 214500},
    {"id": 3, "modelo": "R15 V4", "marca": "Yamaha", "cilindraje": "155 cc", "disponibles": 8, "precio": 105000},
]

def es_admin(request):
    role = request.headers.get("X-User-Role")
    return role == "admin"

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
    USUARIOS[email] = {
    "password": password,
    "role": "user",
    "carrito": [] 
}

    
    # print(f"Nuevo usuario registrado: {email}. Total de usuarios: {len(USUARIOS)}") # Comentado para evitar posibles I/O errors en Render
    return jsonify({
        "mensaje": "Registro exitoso. Ahora puedes iniciar sesión.",
        "usuario": email
    }), 201 

@app.route('/api/login', methods=['POST'])
def login_usuario():
    try:
        datos_login = request.get_json()
    except Exception:
        return jsonify({"mensaje": "Error en la petición"}), 400
        
    if not datos_login or 'email' not in datos_login or 'password' not in datos_login:
        return jsonify({"mensaje": "Email y contraseña son requeridos"}), 400
    
    email = datos_login['email']
    password = datos_login['password']
    
    if email in USUARIOS and USUARIOS[email]["password"] == password:
        #  DEFINICIÓN DEL ROL 
        role = USUARIOS[email]["role"]

        return jsonify({
            "mensaje": "Inicio de sesión exitoso",
            "token": f"fake_jwt_{email}_hash",
            "usuario": email,
            "role": role
        }), 200
    else:
        return jsonify({"mensaje": "Credenciales inválidas"}), 401

@app.route('/api/inventario', methods=['GET'])
def obtener_inventario():
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    return jsonify(INVENTARIO)

@app.route('/api/inventario', methods=['POST'])
def crear_moto():
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    data = request.get_json()
    nuevo_id = max(m["id"] for m in INVENTARIO) + 1

    nueva_moto = {
        "id": nuevo_id,
        "modelo": data["modelo"],
        "marca": data["marca"],
        "cilindraje": data["cilindraje"],
        "disponibles": data["disponibles"],
        "precio": data["precio"]
    }

    INVENTARIO.append(nueva_moto)
    return jsonify(nueva_moto), 201



@app.route('/api/inventario/<int:id>', methods=['PUT'])
def editar_moto(id):
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    data = request.get_json()

    for moto in INVENTARIO:
        if moto["id"] == id:
            moto.update(data)
            return jsonify(moto)

    return jsonify({"mensaje": "Moto no encontrada"}), 404


@app.route('/api/inventario/<int:id>', methods=['DELETE'])
def eliminar_moto(id):
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    global INVENTARIO
    INVENTARIO = [m for m in INVENTARIO if m["id"] != id]
    return jsonify({"mensaje": "Moto eliminada"})

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    lista_usuarios = []

    for email, data in USUARIOS.items():
     lista_usuarios.append({
        "email": email,
        "role": data["role"]
    })


    return jsonify(lista_usuarios)


@app.route('/api/usuarios', methods=['POST'])
def crear_usuario():
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "user")

    if email in USUARIOS:
        return jsonify({"mensaje": "Usuario ya existe"}), 409

    USUARIOS[email] = {
        "password": password,
        "role": role,
        "carrito": []
    }

    return jsonify({"mensaje": "Usuario creado"}), 201

@app.route('/api/usuarios/<email>', methods=['PUT'])
def editar_usuario(email):
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    if email not in USUARIOS:
        return jsonify({"mensaje": "Usuario no encontrado"}), 404

    data = request.get_json()
    USUARIOS[email]["role"] = data.get("role", "user")

    return jsonify({"mensaje": "Usuario actualizado"})

@app.route('/api/usuarios/<email>', methods=['DELETE'])
def eliminar_usuario(email):
    if not es_admin(request):
        return jsonify({"mensaje": "Acceso denegado"}), 403

    if email == "admin@motopower.com":
        return jsonify({"mensaje": "No puedes eliminar al admin"}), 400

    USUARIOS.pop(email, None)
    return jsonify({"mensaje": "Usuario eliminado"})



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


@app.route('/api/carrito', methods=['GET'])
def obtener_carrito():
    email = request.headers.get("X-User-Email")

    if not email or email not in USUARIOS:
        return jsonify({"mensaje": "No autorizado"}), 401

    return jsonify(USUARIOS[email]["carrito"])


@app.route('/api/carrito', methods=['POST'])
def agregar_carrito():
    email = request.headers.get("X-User-Email")
    data = request.get_json()

    if not email or email not in USUARIOS:
        return jsonify({"mensaje": "No autorizado"}), 401

    USUARIOS[email]["carrito"].append(data)
    return jsonify({"mensaje": "Producto agregado"})

@app.route('/api/carrito', methods=['DELETE'])
def vaciar_carrito():
    email = request.headers.get("X-User-Email")

    if not email or email not in USUARIOS:
        return jsonify({"mensaje": "No autorizado"}), 401

    USUARIOS[email]["carrito"] = []
    return jsonify({"mensaje": "Carrito vacío"})


@app.route('/')
def index():
    return render_template('index.html')
# =========================================================================
# INICIO DEL SERVIDOR
# =========================================================================
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template("404.html"), 404


if __name__ == '__main__':
    # Usar host 0.0.0.0 y puerto 5000 para despliegue y pruebas locales
    app.run(host='0.0.0.0', port=5000, debug=True)


    
