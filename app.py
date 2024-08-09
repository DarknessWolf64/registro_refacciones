from flask import Flask, request, jsonify, render_template, redirect, url_for
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            return jsonify({"message": "All fields are required"}), 400
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", 
                           (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return jsonify({"message": "Username or email already exists"}), 400
    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            return redirect(url_for('data'))
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    
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

@app.route('/eliminar_registro/<int:id>', methods=['POST'])
def eliminar_registro(id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refacciones WHERE ID = ?", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for('data'))
    except:
        return jsonify({"message": "Error al eliminar el registro"}), 500

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
            return jsonify({"message": "All fields are required"}), 400
         
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO refacciones (NUMERO_DE_PARTE, DESCRIPCION, COSTO_LISTA, COSTO_INSTALACION, TOTAL_CON_IVA, CUMPLE) VALUES (?, ?, ?, ?, ?, ?)", 
                           (NUMERO_DE_PARTE, DESCRIPCION, COSTO_LISTA, COSTO_INSTALACION, TOTAL_CON_IVA, CUMPLE))
            conn.commit()
            conn.close()
            return redirect(url_for('insertar'))
        except sqlite3.IntegrityError:
            return jsonify({"message": "datos ya ingresados"}), 400
    return render_template('insertar.html')

@app.route('/modificar_registro/<int:id>', methods=['POST'])
def modificar_registro(id):
    data = request.json
    NUMERO_DE_PARTE = data.get('numero_parte')
    DESCRIPCION = data.get('descripcion')
    COSTO_LISTA = data.get('costo_lista')
    COSTO_INSTALACION = data.get('costo_instalacion')
    TOTAL_CON_IVA = data.get('total_iva')
    CUMPLE = data.get('cumple')

    if not NUMERO_DE_PARTE or not DESCRIPCION or not COSTO_LISTA or not COSTO_INSTALACION or not TOTAL_CON_IVA or not CUMPLE:
        return jsonify({"message": "All fields are required"}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE refacciones
            SET NUMERO_DE_PARTE = ?, DESCRIPCION = ?, COSTO_LISTA = ?, COSTO_INSTALACION = ?, TOTAL_CON_IVA = ?, CUMPLE = ?
            WHERE ID = ?
        ''', (NUMERO_DE_PARTE, DESCRIPCION, COSTO_LISTA, COSTO_INSTALACION, TOTAL_CON_IVA, CUMPLE, id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Registro modificado exitosamente"}), 200
    except:
        return jsonify({"message": "Error al modificar el registro"}), 500

@app.route('/dashboard',methods=['GET'])
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
