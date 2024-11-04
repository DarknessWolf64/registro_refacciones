from flask import Flask, request, render_template, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def create_user_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def create_ref_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refacciones (
            ID INTEGER PRIMARY KEY,
            NUMERO_DE_PARTE TEXT NOT NULL,
            DESCRIPCION TEXT NOT NULL,
            COSTO_LISTA REAL NOT NULL,
            COSTO_INSTALACION REAL NOT NULL,
            TOTAL_CON_IVA REAL NOT NULL,
            CUMPLE TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def alert_message(message, redirect_url='/'):
    return f"<script>alert('{message}'); window.location.href='{redirect_url}';</script>"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            return alert_message("Todos los campos son obligatorios.")

        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            return alert_message("Registro exitoso. Redirigiendo al inicio de sesión...", '/')
        except sqlite3.IntegrityError:
            return alert_message("El nombre de usuario o correo ya existe.")
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            return alert_message("El correo y la contraseña son obligatorios.")

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            return alert_message("Inicio de sesión exitoso. Redirigiendo...", '/data')
        else:
            return alert_message("Correo o contraseña incorrectos.")
    
    return render_template('login.html')

@app.route('/data', methods=['GET'])
def data():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refacciones")
    refacciones = cursor.fetchall()
    conn.close()

    refacciones_array = [{"ID": refaccion[0], "NUMERO_DE_PARTE": refaccion[1], "DESCRIPCION": refaccion[2], "COSTO_LISTA": refaccion[3], "COSTO_INSTALACION": refaccion[4], "TOTAL_CON_IVA": refaccion[5], "CUMPLE": refaccion[6]} for refaccion in refacciones]

    return render_template('data.html', refacciones=refacciones_array)

@app.route('/modificar/<int:id>', methods=['PUT'])
def modificar_registro(id):
    data = request.form
    numero_parte = data.get('numero_parte')
    descripcion = data.get('descripcion')
    costo_lista = data.get('costo_lista')
    costo_instalacion = data.get('costo_instalacion')
    total_iva = data.get('total_iva')
    cumple = data.get('cumple')

    # Aquí deberías agregar la lógica para modificar el registro en la base de datos
    try:
        # Supongamos que tienes una función llamada `actualizar_registro` para modificar el registro
        with DATABASE.connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                UPDATE refacciones SET
                    NUMERO_DE_PARTE = %s,
                    DESCRIPCION = %s,
                    COSTO_LISTA = %s,
                    COSTO_INSTALACION = %s,
                    TOTAL_CON_IVA = %s,
                    CUMPLE = %s
                WHERE ID = %s
            ''', (numero_parte, descripcion, costo_lista, costo_instalacion, total_iva, cumple, id))
            connection.commit()

        return alert_message("Registro modificado con éxito")
    except Exception as e:
        return alert_message(f"Error al modificar el registro: {str(e)}")

@app.route('/eliminar', methods=['POST'])
def eliminar_registro():
    try:
        # Obtener el ID del registro desde el cuerpo de la solicitud
        data = request.get_json()  # Se espera que el cuerpo sea en formato JSON
        id = data.get('id')  # Obtener el ID

        if id is None:
            return alert_message("ID no proporcionado")

        with DATABASE.connection() as connection:
            cursor = connection.cursor()
            # Verificar si el registro existe antes de intentar eliminarlo
            cursor.execute('SELECT * FROM refacciones WHERE ID = %s', (id,))
            if cursor.fetchone() is None:
                return alert_message("Registro no encontrado")
            
            # Intentar eliminar el registro
            cursor.execute('DELETE FROM refacciones WHERE ID = %s', (id,))
            connection.commit()

        return alert_message("Registro eliminado con éxito")
    except Exception as e:
        return alert_message(f"Error al eliminar el registro: {str(e)}")


@app.route('/insertar_data', methods=['GET', 'POST'])
def insertar():
    if request.method == 'POST':
        NUMERO_DE_PARTE = request.form['num_parte']
        DESCRIPCION = request.form['descripcion']
        COSTO_LISTA = request.form['costo_lista']
        COSTO_INSTALACION = request.form['costo_instalacion']
        TOTAL_CON_IVA = request.form['total_con_iva']
        CUMPLE = request.form['cumple']

        if not NUMERO_DE_PARTE or not DESCRIPCION or not COSTO_LISTA or not COSTO_INSTALACION or not TOTAL_CON_IVA or not CUMPLE:
            return alert_message("Todos los campos son obligatorios.")
         
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO refacciones (NUMERO_DE_PARTE, DESCRIPCION, COSTO_LISTA, COSTO_INSTALACION, TOTAL_CON_IVA, CUMPLE) VALUES (?, ?, ?, ?, ?, ?)", 
                           (NUMERO_DE_PARTE, DESCRIPCION, COSTO_LISTA, COSTO_INSTALACION, TOTAL_CON_IVA, CUMPLE))
            conn.commit()
            conn.close()
            return alert_message("Registro insertado correctamente.", '/insertar_data')
        except sqlite3.IntegrityError:
            return alert_message("Los datos ya existen.")
    return render_template('insertar.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refacciones")
    refacciones = cursor.fetchall()
    conn.close()
    
    refacciones_array = [{"ID": refaccion[0], "NUMERO_DE_PARTE": refaccion[1], "DESCRIPCION": refaccion[2], "COSTO_LISTA": refaccion[3], "COSTO_INSTALACION": refaccion[4], "TOTAL_CON_IVA": refaccion[5], "CUMPLE": refaccion[6]} for refaccion in refacciones]

    return render_template('dashboard.html', refacciones=refacciones_array)

if __name__ == '__main__':
    create_user_table()
    create_ref_table()
    app.run(debug=True, host='0.0.0.0')
