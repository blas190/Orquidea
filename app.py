# app.py

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS 
from flask import request, jsonify
from flask import Flask, request, jsonify, session
import unicodedata
import re
import requests
from flask_mail import Mail, Message
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random
app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ivanricardo65@gmail.com'
app.config['MAIL_PASSWORD'] = 'sbcs vtpa freo ibdz'


mail = Mail(app)
CORS(app) 

# Configuración de reCAPTCHA
app.config['RECAPTCHA_SITE_KEY'] = '6LeaWuAsAAAAALVL1Qc32QlPpZdnHUhsw76HX4Pt'
app.config['RECAPTCHA_SECRET_KEY'] = '6LeaWuAsAAAAACqQpZ9YL9qXY_DhNcZXC0KM-SRk'

# Función para verificar reCAPTCHA manualmente
def verificar_recaptcha(recaptcha_response):
    """Verifica el token de reCAPTCHA v2 con Google"""
    if not recaptcha_response:
        return False
    
    verify_url = 'https://www.google.com/recaptcha/api/siteverify'
    payload = {
        'secret': app.config['RECAPTCHA_SECRET_KEY'],
        'response': recaptcha_response
    }
    
    try:
        response = requests.post(verify_url, data=payload, timeout=5)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"Error verificando reCAPTCHA: {e}")
        return False 
# ==========================================================
# 🏍️ INVENTARIO REAL
# ==========================================================

INVENTARIO = [
    {"id": 1, "modelo": "Z900", "marca": "Kawasaki", "cilindraje": 948, "precio": 259900, "tipo": "deportiva"},
    {"id": 2, "modelo": "CB650R", "marca": "Honda", "cilindraje": 649, "precio": 214500, "tipo": "deportiva"},
    {"id": 3, "modelo": "R15 V4", "marca": "Yamaha", "cilindraje": 155, "precio": 105000, "tipo": "economica"},
    {"id": 4, "modelo": "FT150", "marca": "Italika", "cilindraje": 150, "precio": 22000, "tipo": "trabajo"},
    {"id": 5, "modelo": "D125", "marca": "Italika", "cilindraje": 125, "precio": 18000, "tipo": "economica"}
]

# ==========================================================
# 🧠 NORMALIZAR TEXTO
# ==========================================================

def limpiar_texto(texto):
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

def es_correo_valido(correo):

    if len(correo) > 254:
        return False

    patron = (
        r"^(?!.*\.\.)"
        r"[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    return re.match(patron, correo) is not None
# ==========================================================
# 🧠 DETECTAR INTENCIÓN
# ==========================================================

def detectar_intencion(msg):
    if any(x in msg for x in ["hola", "buenas", "hey","hello", "hi"]):
        return "saludo"
    elif any(x in msg for x in ["catalogo", "catálogo", "ver motos", "todas las motos", "que tienes", "inventario"]):
        return "catalogo"
    elif any(x in msg for x in ["ayuda", "help", "no se", "no entiendo", "que puedes hacer"]):
        return "ayuda"
    elif any(x in msg for x in ["ayuda", "help", "no se", "no entiendo", "que puedes hacer"]):
        return "ayuda"
    elif any(x in msg for x in ["donde estan", "ubicacion", "direccion", "dónde se ubican", "donde queda", "local"]):
        return "ubicacion"
    elif any(x in msg for x in ["envio", "envios", "entrega", "mandan", "delivery"]):
        return "envios"
    elif any(x in msg for x in ["devolucion", "garantia", "reembolso", "cambio"]):
        return "devoluciones"
    elif any(x in msg for x in ["pago", "pagos", "metodos de pago", "tarjeta", "transferencia", "efectivo"]):
        return "pagos"
    elif any(x in msg for x in ["promocion", "promociones", "descuento", "oferta"]):
        return "promociones"
    elif any(x in msg for x in ["gracias", "ok", "vale", "perfecto", "adios", "nos vemos", "bye"]):
        return "despedida"
    elif any(x in msg for x in ["comprar", "busco", "quiero"]):
        return "compra"
    elif any(x in msg for x in ["economica", "barata"]):
        return "economica"
    elif any(x in msg for x in ["deportiva", "deportivo"]):
        return "deportiva"
    elif any(x in msg for x in ["trabajo", "reparto"]):
        return "trabajo"
    elif any(x in msg for x in ["horario"]):
        return "horario"
    elif any(x in msg for x in ["contacto", "correo","telefono", "numero telefonico"]):
        return "contacto"
    elif any(x in msg for x in ["precio", "cuanto"]):
        return "precio"
    elif any(x in msg for x in ["yamaha", "honda", "italika", "kawasaki"]):
        return "marca"
    elif any(x in msg for x in ["me interesa", "la quiero", "comprar esa"]):
        return "cierre"
    elif any(x in msg for x in ["donde estan", "ubicacion", "direccion", "dónde se ubican", "donde queda", "local"]):
        return "ubicacion"
    elif any(x in msg for x in ["gracias", "ok", "vale", "perfecto", "adios", "nos vemos", "bye"]):
        return "despedida"
    elif any(x in msg for x in ["comprar", "busco", "quiero"]):
        return "compra"
    elif any(x in msg for x in ["economica", "barata"]):
        return "economica"
    elif any(x in msg for x in ["deportiva", "deportivo"]):
        return "deportiva"
    elif any(x in msg for x in ["trabajo", "reparto"]):
        return "trabajo"
    elif any(x in msg for x in ["precio", "cuanto"]):
        return "precio"
    elif any(x in msg for x in ["yamaha", "honda", "italika", "kawasaki"]):
        return "marca"
    elif any(x in msg for x in ["me interesa", "la quiero", "comprar esa"]):
        return "cierre"
    else:
        return "otro"

# ==========================================================
# 🔎 FILTRAR MOTOS
# ==========================================================
# normalizar tipo


def filtrar_motos(tipo=None, marca=None, presupuesto=None):
    resultados = INVENTARIO
    # normalizar tipo
  

    if tipo:
        resultados = [m for m in resultados if m.get("tipo") == tipo]

    if marca:
        resultados = [m for m in resultados if marca in m.get("marca", "").lower()]

    if presupuesto:
        resultados = [m for m in resultados if m.get("precio", 0) <= presupuesto]

    return resultados

# ==========================================================
# 💬 FORMATEAR RESPUESTA
# ==========================================================

def mostrar_motos(lista):
    if not lista:
        return "😅 No encontré motos con esas características."

    texto = "🏍️ Opciones disponibles:\n"
    for m in lista:
        texto += f"- {m['marca']} {m['modelo']} (${m['precio']})\n"
    return texto

# ==========================================================
# 💬 RESPONDER
# ==========================================================

def responder(msg):
    intent = detectar_intencion(msg)

    # 🔥 detectar presupuesto
    palabras = msg.split()
    presupuesto = None
    for p in palabras:
        if p.isdigit():
            presupuesto = int(p)

    # 🔥 detectar marca
    marca = None
    for m in ["yamaha", "honda", "italika", "kawasaki"]:
        if m in msg:
            marca = m
    

    # 🔥 detectar tipo
    tipo = None
    if any(x in msg for x in ["economica", "barata"]):
        tipo = "economica"
    elif any(x in msg for x in ["deportiva", "deportivo"]):
        tipo = "deportiva"
    elif any(x in msg for x in ["trabajo", "reparto"]):
        tipo = "trabajo"
    
    # =====================================================
    # 🔥 PRIORIDAD: FILTROS (más inteligente)

    if tipo or marca or presupuesto:
        motos = filtrar_motos(tipo=tipo, marca=marca, presupuesto=presupuesto)

        texto = "🏍️ Opciones para ti:\n"

        tipo_mostrar = {
    "economica": "Económica 💰",
    "deportiva": "Deportiva 🔥",
    "trabajo": "Trabajo 💼"
}

        if tipo:
            texto += f"👉 Tipo: {tipo_mostrar.get(tipo, tipo)}\n"
        if marca:
            texto += f"👉 Marca: {marca}\n"
        if presupuesto:
            texto += f"👉 Presupuesto: ${presupuesto}\n"

        return texto + "\n" + mostrar_motos(motos)

    # =====================================================

    if intent == "saludo":
        return "¡Hola! 🏍️ ¿Qué tipo de moto buscas? (económica, deportiva o trabajo)"
    
    elif intent == "compra":
        return "Perfecto 😎 ¿Para qué la necesitas? (trabajo, ciudad o velocidad)"
    elif intent == "ayuda":
        return (
        "😎 ¡Claro! Estoy para ayudarte a elegir tu moto ideal 🏍️\n\n"
        "Puedes decirme:\n"
        "💰 Tu presupuesto → 'tengo 50000'\n"
        "🔥 Tipo de moto → 'deportiva', 'económica', 'trabajo'\n"
        "🏷️ Marca → 'yamaha', 'honda', 'italika'\n\n"
        "O simplemente escribe algo como:\n"
        "👉 'quiero una moto barata'\n\n"
        "🔥 Yo te muestro opciones al instante\n\n"
        "¿Qué buscas?"
    )
    elif intent == "ubicacion":
        return (
        "📍 MotoPower - Sucursal CDMX\n"
        "Calle Ejemplo 123, Col. Centro 🏙️\n\n"
        "🗺️ Ver en mapa:\n"
        "https://maps.google.com/?q=Calle+Ejemplo+123+CDMX\n\n"
        "🕒 Horario:\n"
        "Lunes a Sábado: 10am - 7pm\n\n"
        "🔥 Puedes venir a ver, probar y apartar tu moto el mismo día\n\n"
        "👉 ¿A qué hora te gustaría venir?"
    )
    elif intent == "precio":
        return "Tenemos motos desde $18,000 hasta $259,900 💰 ¿Cuál es tu presupuesto?"
    elif intent == "contacto":
        return "encuentranos en redes sociales como MOTOPOWER, por correo como motopower@hotmail.com o por numero celular al 5521365911"

    elif intent == "catalogo":
        return (
        "📋 Este es nuestro catálogo completo 🏍️🔥\n\n"
        + mostrar_motos(INVENTARIO) +
        "\n\n👉 Puedes filtrar por:\n"
        "💰 Precio\n"
        "🔥 Tipo (deportiva, económica, trabajo)\n"
        "🏷️ Marca\n\n"
        "Ejemplo: 'yamaha deportiva 100000'"
    )

    elif intent == "cierre":
        return "🔥 Excelente elección, ¿quieres que apartemos la moto o agendamos visita?"

    elif intent == "despedida":
        return (
        "🙌 ¡Gracias por visitar MotoPower! 🏍️\n"
        "Si más adelante buscas una moto, aquí estaré para ayudarte 😎\n\n"
        "🔥 Recuerda: tenemos opciones económicas, deportivas y de trabajo\n"
        "¡Que tengas un excelente día!"
         )
    elif intent == "envios":
        return (
        "🚚 Hacemos envíos a todo México 🇲🇽\n\n"
        "📦 Tiempo de entrega: 3 a 7 días hábiles\n"
        "💰 Costo depende de tu ubicación\n\n"
        "👉 Dime tu ciudad y te cotizo el envío 😉"
    )

    elif intent == "devoluciones":
        return (
        "🔄 Contamos con garantía en todas nuestras motos 🏍️\n\n"
        "🛠️ Garantía por defectos de fábrica\n"
        "📅 Aplica dentro de los primeros días\n\n"
        "👉 Si tienes algún problema, te apoyamos directamente 👍"
    )
    


    elif intent == "horario":
        return (
        "🕒 Horario:\n"
        "Lunes a Sábado: 10am - 7pm\n\n"
        "🔥 Puedes venir a ver, probar y apartar tu moto el mismo día\n\n"
        "👉 ¿A qué hora te gustaría venir?"
    )

    elif intent == "pagos":
        return (
        "💳 Métodos de pago disponibles:\n\n"
        "✔️ Efectivo\n"
        "✔️ Transferencia bancaria\n"
        "✔️ Tarjeta de crédito/débito\n\n"
        "🔥 También manejamos meses sin intereses en algunos modelos\n\n"
        "👉 ¿Cómo te gustaría pagar?"
    )

    elif intent == "promociones":
        return (
        "🔥 Tenemos promociones activas:\n\n"
        "💸 Descuentos en motos seleccionadas\n"
        "📅 Meses sin intereses\n"
        "🎁 Bonos en accesorios\n\n"
        "👉 Dime qué tipo de moto buscas y te digo si aplica promo 😉"
    )
    else:
        return (
        "🤔 No entendí del todo, pero puedo ayudarte 🏍️\n\n"
        "Puedes preguntarme cosas como:\n"
        "💰 'moto barata de 50000'\n"
        "🔥 'deportiva yamaha'\n"
        "💼 'moto para trabajo'\n"
        "🚚 'hacen envíos'\n"
        "💳 'formas de pago'\n"
        "🎁 'tienen promociones'\n\n"
        "👉 ¿Qué estás buscando?"
)
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = limpiar_texto(data.get('message', ''))

        if not user_message:
            return jsonify({"response": "¿Qué moto estás buscando? 🏍️"})

        response = responder(user_message)

        return jsonify({"response": response})

    except Exception as e:
        print("🔥 ERROR REAL:", e)
        return jsonify({"response": str(e)})



USUARIOS = {

    "admin@motopower.com": {
        "password": generate_password_hash("password123"),
        "role": "admin",
        "carrito": []
    }
}



def es_admin(request):
    role = request.headers.get("X-User-Role")
    return role == "admin"

MENSAJES = []
CODIGOS_VERIFICACION = {}
CODIGOS_2FA = {}  # Nuevo diccionario para códigos de 2FA
EMAILS_VERIFICADOS = {"admin@motopower.com"}
# =========================================================================
# FUNCIONES AUXILIARES
# =========================================================================

def limpiar_codigos_expirados():
    """Limpia códigos 2FA expirados (más de 5 minutos)"""
    ahora = datetime.datetime.now()
    expirados = []
    for email, datos in CODIGOS_2FA.items():
        tiempo_transcurrido = ahora - datos['timestamp']
        if tiempo_transcurrido.total_seconds() > 300:
            expirados.append(email)
    
    for email in expirados:
        del CODIGOS_2FA[email]

# =========================================================================
# ENDPOINTS DE LA API
# =========================================================================
@app.route('/api/enviar-codigo', methods=['POST'])
def enviar_codigo():

    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({
            "mensaje": "Correo requerido"
        }), 400

    if not es_correo_valido(email):
        return jsonify({
            "mensaje": "Correo inválido"
        }), 400

    codigo = str(random.randint(100000, 999999))

    CODIGOS_VERIFICACION[email] = codigo

    try:

        mensaje = Message(
            "Código de verificación MotoPower",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )

        mensaje.body = f"""
Tu código de verificación es:

{codigo}

No compartas este código.
"""

        mail.send(mensaje)

        return jsonify({
            "mensaje": "Código enviado al correo"
        })

    except Exception as e:
        print(e)

        return jsonify({
            "mensaje": "Error enviando correo"
        }), 500
@app.route('/api/verificar-codigo', methods=['POST'])
def verificar_codigo():

    data = request.get_json()

    email = data.get("email")
    codigo = data.get("codigo")

    codigo_guardado = CODIGOS_VERIFICACION.get(email)

    if not codigo_guardado:
        return jsonify({
            "mensaje": "No hay código generado"
        }), 400

    if codigo != codigo_guardado:
        return jsonify({
            "mensaje": "Código incorrecto"
        }), 401

    del CODIGOS_VERIFICACION[email]
    EMAILS_VERIFICADOS.add(email)

    return jsonify({
        "mensaje": "Correo verificado correctamente"
    })
@app.route('/api/verificar-2fa', methods=['POST'])
def verificar_2fa():
    data = request.get_json()
    
    email = data.get("email")
    codigo = data.get("codigo")
    
    if not email or not codigo:
        return jsonify({"mensaje": "Email y código son requeridos"}), 400
    
    # Limpiar códigos expirados
    limpiar_codigos_expirados()
    
    datos_codigo = CODIGOS_2FA.get(email)
    
    if not datos_codigo:
        return jsonify({"mensaje": "No hay código 2FA pendiente"}), 400
    
    # Verificar expiración (5 minutos)
    tiempo_transcurrido = datetime.datetime.now() - datos_codigo['timestamp']
    if tiempo_transcurrido.total_seconds() > 300:  # 300 segundos = 5 minutos
        del CODIGOS_2FA[email]
        return jsonify({"mensaje": "Código 2FA expirado. Solicita uno nuevo."}), 401
    
    if codigo != datos_codigo['codigo']:
        return jsonify({"mensaje": "Código 2FA incorrecto"}), 401
    
    # Código correcto, completar login
    del CODIGOS_2FA[email]
    
    role = USUARIOS[email]["role"]
    
    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": f"fake_jwt_{email}_hash",
        "usuario": email,
        "role": role
    }), 200
        
@app.route('/api/register', methods=['POST'])
def register_usuario():
    """Simula el registro de un nuevo usuario con validación de correo y reCAPTCHA."""
    
    try:
        datos = request.get_json()
    except Exception:
        return jsonify({"mensaje": "Error en la petición: Asegúrate de que estás enviando JSON válido."}), 400

    if not datos:
        return jsonify({"mensaje": "Error: El cuerpo de la petición está vacío o no es JSON."}), 400

    # 1. Extraer datos básicos
    email = datos.get('email', '').strip()
    password = datos.get('password', '').strip()
    if (
    len(password) < 8 or
    not re.search(r"[A-Z]", password) or
    not re.search(r"[a-z]", password) or
    not re.search(r"\d", password)
):
        return jsonify({
        "mensaje": "La contraseña debe incluir mayúscula, minúscula y número"
    }), 400
    recaptcha_token = datos.get('g-recaptcha-response', '')

    # 2. Validación de presencia de campos obligatorios
    if not email or not password:
        return jsonify({"mensaje": "Email y contraseña son requeridos para el registro."}), 400

    # 3. NUEVA: Validación de formato de correo electrónico
    if not es_correo_valido(email):
        return jsonify({"mensaje": "Error: El formato del correo electrónico no es válido."}), 400

    # 4. Verificar que el correo ya haya sido confirmado por Gmail
    if email not in EMAILS_VERIFICADOS:
        return jsonify({"mensaje": "Debes verificar tu correo con el código enviado antes de registrarte."}), 400

    # 5. Verificar reCAPTCHA (Seguridad)
    try:
        if not verificar_recaptcha(recaptcha_token):
            return jsonify({"mensaje": "Verificación de reCAPTCHA fallida. Por favor, intenta de nuevo."}), 400
    except Exception as e:
        print(f"Error en verificación de reCAPTCHA: {e}")
        return jsonify({"mensaje": "Error en la verificación de seguridad."}), 400

    # 6. Verificar si el usuario ya existe en el sistema
    if email in USUARIOS:
        return jsonify({"mensaje": f"El email {email} ya está registrado."}), 409 

    # 6. Realizar el registro en el diccionario de USUARIOS
    USUARIOS[email] = {
        "password": generate_password_hash(password),
        "role": "user",
        "carrito": [] 
    }

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

    if not es_correo_valido(email):
        return jsonify({"mensaje": "Correo inválido"}), 400

    if email not in EMAILS_VERIFICADOS:
        return jsonify({"mensaje": "Debes verificar tu correo antes de iniciar sesión."}), 401
    
    if (
    email in USUARIOS and
    check_password_hash(USUARIOS[email]["password"], password)
    
):
        # Generar código 2FA
        codigo_2fa = str(random.randint(100000, 999999))
        CODIGOS_2FA[email] = {
            'codigo': codigo_2fa,
            'timestamp': datetime.datetime.now()
        }
        
        # Enviar código por email
        try:
            mensaje = Message(
                "Código de verificación de dos pasos - MotoPower",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            
            mensaje.body = f"""
Hola,

Alguien está intentando acceder a tu cuenta en MotoPower.

Tu código de verificación de dos pasos es:

{codigo_2fa}

Ingresa este código para completar el inicio de sesión.

Si no fuiste tú, ignora este mensaje.

Saludos,
Equipo MotoPower
"""
            
            mail.send(mensaje)
            
            return jsonify({
                "mensaje": "Credenciales válidas. Código 2FA enviado al correo.",
                "requiere_2fa": True,
                "usuario": email
            }), 200
            
        except Exception as e:
            print(f"Error enviando 2FA: {e}")
            return jsonify({"mensaje": "Error enviando código de verificación"}), 500
            
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
    
    # Obtener y validar datos del contacto
    try:
        datos_contacto = request.get_json()
    except Exception:
        return jsonify({"mensaje": "Error en la petición: El cuerpo de la solicitud no es JSON válido."}), 400
    
    if not datos_contacto or 'nombre' not in datos_contacto or 'correo' not in datos_contacto or 'mensaje' not in datos_contacto:
        return jsonify({"mensaje": "Datos incompletos"}), 400
    
    MENSAJES.append(datos_contacto)
    
    return jsonify({"mensaje": "¡Gracias! Hemos recibido tu mensaje."}), 201


@app.route('/api/recaptcha-key', methods=['GET'])
def obtener_recaptcha_key():
    """Devuelve la clave pública de reCAPTCHA para el frontend"""
    return jsonify({"siteKey": app.config['RECAPTCHA_SITE_KEY']})


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
# ==========================================================
# 🛒 NUEVOS ENDPOINTS: COMPRA Y QUIÉNES SOMOS
# ==========================================================

@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Procesa el intento de compra y redirige a PayPal"""
    # El backend busca este encabezado para saber qué usuario compra
    email = request.headers.get("X-User-Email")
    
    if not email or email not in USUARIOS:
        return jsonify({"mensaje": "Error: Debes iniciar sesión para comprar"}), 401
    
    # Si el carrito está vacío, no permitir compra
    if not USUARIOS[email]["carrito"]:
        return jsonify({"mensaje": "Tu carrito está vacío"}), 400

    # Simulamos la respuesta para PayPal
    return jsonify({
        "mensaje": "Iniciando proceso de pago seguro...",
        "url": "https://www.paypal.com/checkout" 
    })

@app.route('/api/nosotros', methods=['GET'])
def obtener_nosotros():
    return jsonify({
        "mensaje": "🌟 En MotoPower somos apasionados por las dos ruedas.\n"
                    "Nos dedicamos a ofrecer las mejores motos en CDMX, desde modelos "
                    "económicos para trabajo hasta potentes deportivas."
    })

if __name__ == '__main__':
    # Usar host 0.0.0.0 y puerto 5000 para despliegue y pruebas locales
    app.run(host='0.0.0.0', port=5000, debug=True)


    
