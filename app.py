from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
# Llave secreta para habilitar la firma de cookies de sesión
app.secret_key = 'RootHosting_2021'

# Configuración de base de datos MySQL por defecto
# Adapta estos parámetros si tu base de datos tiene otro usuario, contraseña, o nombre
DB_HOST = 'roothosting.myddns.me'
DB_USER = 'root'
DB_PASSWORD = 'RootHosting_2021'
DB_NAME = 'flask-db'

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

@app.route('/')
def home():
    conn = get_db_connection()
    if not conn:
        flash("No se pudo conectar a la base de datos.", "error")
        return render_template('index.html', juegos=[])
    
    cursor = conn.cursor(dictionary=True)
    
    query = """
    SELECT v.id, v.titulo, v.imagen_url, d.nombre as desarrollador,
           GROUP_CONCAT(p.nombre SEPARATOR ', ') as plataformas,
           (SELECT COUNT(*) FROM resenas r WHERE r.videojuego_id = v.id) as total_resenas,
           (SELECT AVG(calificacion) FROM resenas r WHERE r.videojuego_id = v.id) as avg_rating
    FROM videojuegos v
    LEFT JOIN desarrolladores d ON v.desarrollador_id = d.id
    LEFT JOIN videojuego_plataforma vp ON v.id = vp.videojuego_id
    LEFT JOIN plataformas p ON vp.plataforma_id = p.id
    GROUP BY v.id
    """
    cursor.execute(query)
    juegos = cursor.fetchall()
    
    # Manejar promedios nulos
    for j in juegos:
        if j['avg_rating'] is None:
            j['avg_rating'] = 0.0
        else:
            j['avg_rating'] = round(float(j['avg_rating']), 1)
        
        if j['plataformas']:
            j['plataformas_list'] = j['plataformas'].split(', ')
        else:
            j['plataformas_list'] = []
            
    conn.close()
    return render_template('index.html', juegos=juegos)

@app.route('/plataformas')
def plataformas():
    conn = get_db_connection()
    if not conn:
        return "Error DB"
        
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nombre, p.imagen_url, COUNT(vp.videojuego_id) as total_juegos
        FROM plataformas p
        LEFT JOIN videojuego_plataforma vp ON p.id = vp.plataforma_id
        GROUP BY p.id
        ORDER BY p.nombre ASC
    """)
    lista_plataformas = cursor.fetchall()
    conn.close()
    
    return render_template('plataformas.html', plataformas=lista_plataformas)

@app.route('/plataforma/<int:id>')
def plataforma_detalle(id):
    conn = get_db_connection()
    if not conn:
        return "Error DB"
        
    cursor = conn.cursor(dictionary=True)
    
    # Obtener nombre de plataforma
    cursor.execute("SELECT nombre FROM plataformas WHERE id = %s", (id,))
    plat = cursor.fetchone()
    if not plat:
        return redirect(url_for('plataformas'))
        
    query = """
    SELECT v.id, v.titulo, v.imagen_url, d.nombre as desarrollador,
           GROUP_CONCAT(p.nombre SEPARATOR ', ') as plataformas,
           (SELECT COUNT(*) FROM resenas r WHERE r.videojuego_id = v.id) as total_resenas,
           (SELECT AVG(calificacion) FROM resenas r WHERE r.videojuego_id = v.id) as avg_rating
    FROM videojuegos v
    LEFT JOIN desarrolladores d ON v.desarrollador_id = d.id
    LEFT JOIN videojuego_plataforma vp ON v.id = vp.videojuego_id
    LEFT JOIN plataformas p ON vp.plataforma_id = p.id
    WHERE v.id IN (SELECT videojuego_id FROM videojuego_plataforma WHERE plataforma_id = %s)
    GROUP BY v.id
    """
    cursor.execute(query, (id,))
    juegos = cursor.fetchall()
    
    for j in juegos:
        j['avg_rating'] = round(float(j['avg_rating']), 1) if j['avg_rating'] else 0.0
        j['plataformas_list'] = j['plataformas'].split(', ') if j['plataformas'] else []
            
    conn.close()
    return render_template('plataforma_detalle.html', juegos=juegos, plataforma_nombre=plat['nombre'])

@app.route('/juego/<int:id>')
def juego_detalle(id):
    conn = get_db_connection()
    if not conn:
        flash("Error de base de datos.", "error")
        return redirect(url_for('home'))
        
    cursor = conn.cursor(dictionary=True)
    
    # Info del juego
    cursor.execute("""
        SELECT v.id, v.titulo, v.imagen_url, d.nombre as desarrollador, v.desarrollador_id
        FROM videojuegos v
        LEFT JOIN desarrolladores d ON v.desarrollador_id = d.id
        WHERE v.id = %s
    """, (id,))
    juego = cursor.fetchone()
    
    if not juego:
        flash("Juego no encontrado.", "error")
        return redirect(url_for('home'))
        
    # Plataformas
    cursor.execute("""
        SELECT p.nombre 
        FROM plataformas p
        JOIN videojuego_plataforma vp ON p.id = vp.plataforma_id
        WHERE vp.videojuego_id = %s
    """, (id,))
    juego['plataformas'] = [p['nombre'] for p in cursor.fetchall()]
    
    # Reseñas
    cursor.execute("""
        SELECT r.id, r.calificacion, r.comentario, u.username
        FROM resenas r
        JOIN usuarios u ON r.usuario_id = u.id
        WHERE r.videojuego_id = %s
        ORDER BY r.id DESC
    """, (id,))
    resenas = cursor.fetchall()
    
    # Rating medio
    if resenas:
        juego['avg_rating'] = round(sum(r['calificacion'] for r in resenas) / len(resenas), 1)
    else:
        juego['avg_rating'] = 0.0
        
    conn.close()
    return render_template('juego.html', juego=juego, resenas=resenas)

@app.route('/juego/<int:id>/review', methods=['POST'])
def add_review(id):
    if 'user_id' not in session:
        flash("Debes iniciar sesión para publicar una reseña.", "error")
        return redirect(url_for('login'))
        
    calificacion = int(request.form.get('calificacion', 5))
    comentario = request.form.get('comentario', '')
    
    if not (1 <= calificacion <= 5):
        flash("La calificación debe estar entre 1 y 5.", "error")
        return redirect(url_for('juego_detalle', id=id))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el usuario ya hizo una review para este juego para evitar duplicados si se desea
        # Por ahora permitimos múltiples para pruebas o una según prefieras. Implementaremos una por usuario:
        cursor.execute("SELECT id FROM resenas WHERE usuario_id = %s AND videojuego_id = %s", (session['user_id'], id))
        if cursor.fetchone():
            flash("Ya has publicado una reseña para este título.", "error")
        else:
            cursor.execute("INSERT INTO resenas (usuario_id, videojuego_id, calificacion, comentario) VALUES (%s, %s, %s, %s)",
                       (session['user_id'], id, calificacion, comentario))
            conn.commit()
            flash("Tu reseña ha sido publicada. ¡Gracias!", "success")
    except Exception as e:
        flash(f"Error al guardar la reseña: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('juego_detalle', id=id))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Debes iniciar sesión para ver tu perfil.", "error")
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if not conn:
        flash("Error de base de datos.", "error")
        return redirect(url_for('home'))
        
    cursor = conn.cursor(dictionary=True)
    
    # Obtener info básica del usuario
    cursor.execute("SELECT id, username, email FROM usuarios WHERE id = %s", (session['user_id'],))
    usuario = cursor.fetchone()
    
    # Obtener todas las reviews del usuario (con JOIN al título del juego)
    cursor.execute("""
        SELECT r.id, r.videojuego_id, r.calificacion, r.comentario, v.titulo
        FROM resenas r
        JOIN videojuegos v ON r.videojuego_id = v.id
        WHERE r.usuario_id = %s
        ORDER BY r.id DESC
    """, (session['user_id'],))
    resenas = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', usuario=usuario, resenas=resenas)

@app.route('/dashboard/eliminar_resena/<int:id>', methods=['POST'])
def delete_review(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Importante: Comprobar que la reseña que se intenta borrar le pertenece a este usuario
        cursor.execute("DELETE FROM resenas WHERE id = %s AND usuario_id = %s", (id, session['user_id']))
        if cursor.rowcount > 0:
            conn.commit()
            flash("Tu reseña ha sido eliminada.", "success")
        else:
            flash("No tienes permiso para eliminar esta reseña o no existe.", "error")
    except Exception as e:
        flash("Error al eliminar la reseña.", "error")
    finally:
        conn.close()
        
    return redirect(url_for('dashboard'))

@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        flash("Acceso denegado.", "error")
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Cargar desarrolladores para el formulario de juegos
    cursor.execute("SELECT id, nombre FROM desarrolladores ORDER BY nombre ASC")
    desarrolladores = cursor.fetchall()
    
    # Cargar todos los videojuegos para listarlos
    cursor.execute("SELECT v.id, v.titulo, d.nombre as desarrollador FROM videojuegos v LEFT JOIN desarrolladores d ON v.desarrollador_id = d.id ORDER BY v.id DESC")
    videojuegos = cursor.fetchall()
    
    # Cargar plataformas
    cursor.execute("SELECT id, nombre FROM plataformas ORDER BY nombre ASC")
    plataformas = cursor.fetchall()
    
    # Cargar usuarios que no sean admin para promoverlos
    cursor.execute("SELECT id, username, email FROM usuarios WHERE is_admin = 0 ORDER BY id DESC")
    usuarios = cursor.fetchall()
    
    conn.close()
    return render_template('admin.html', desarrolladores=desarrolladores, usuarios=usuarios, videojuegos=videojuegos, plataformas=plataformas)

@app.route('/admin/add_dev', methods=['POST'])
def add_dev():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    nombre = request.form.get('nombre')
    pais = request.form.get('pais', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO desarrolladores (nombre, pais) VALUES (%s, %s)", (nombre, pais))
        conn.commit()
        flash("Revisión guardada: Desarrolladora agregada con éxito.", "success")
    except Exception as e:
        flash(f"Error al agregar desarrolladora: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_platform', methods=['POST'])
def add_platform():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    nombre = request.form.get('nombre')
    imagen_url = request.form.get('imagen_url', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO plataformas (nombre, imagen_url) VALUES (%s, %s)", (nombre, imagen_url))
        conn.commit()
        flash("Plataforma / Consola agregada exitosamente al catálogo.", "success")
    except Exception as e:
        flash(f"Error al agregar la plataforma: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_platform/<int:id>', methods=['GET', 'POST'])
def edit_platform(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        imagen_url = request.form.get('imagen_url', '')
        
        try:
            cursor.execute("UPDATE plataformas SET nombre=%s, imagen_url=%s WHERE id=%s", (nombre, imagen_url, id))
            conn.commit()
            flash("Plataforma actualizada exitosamente.", "success")
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f"Error al editar: {e}", "error")
            
    cursor.execute("SELECT * FROM plataformas WHERE id = %s", (id,))
    plataforma = cursor.fetchone()
    conn.close()
    
    return render_template('edit_platform.html', plataforma=plataforma)

@app.route('/admin/add_game', methods=['POST'])
def add_game():
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    titulo = request.form.get('titulo')
    dev_id = request.form.get('desarrollador_id')
    imagen_url = request.form.get('imagen_url', '')
    plataformas_sel = request.form.getlist('plataformas')
    
    if not dev_id:
        flash("Debes seleccionar una desarrolladora.", "error")
        return redirect(url_for('admin_dashboard'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO videojuegos (titulo, desarrollador_id, imagen_url) VALUES (%s, %s, %s)", (titulo, dev_id, imagen_url))
        nuevo_juego_id = cursor.lastrowid
        
        # Insertar a la tabla relacional
        if plataformas_sel:
            relaciones = [(nuevo_juego_id, plat_id) for plat_id in plataformas_sel]
            cursor.executemany("INSERT INTO videojuego_plataforma (videojuego_id, plataforma_id) VALUES (%s, %s)", relaciones)
            
        conn.commit()
        flash("Videojuego registrado y enlazado con éxito.", "success")
    except Exception as e:
        flash(f"Error al agregar el juego: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_game/<int:id>', methods=['GET', 'POST'])
def edit_game(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        dev_id = request.form.get('desarrollador_id')
        imagen_url = request.form.get('imagen_url', '')
        plataformas_sel = request.form.getlist('plataformas')
        
        try:
            cursor.execute("UPDATE videojuegos SET titulo=%s, desarrollador_id=%s, imagen_url=%s WHERE id=%s", (titulo, dev_id, imagen_url, id))
            # Refrescar plataformas
            cursor.execute("DELETE FROM videojuego_plataforma WHERE videojuego_id=%s", (id,))
            if plataformas_sel:
                relaciones = [(id, plat_id) for plat_id in plataformas_sel]
                cursor.executemany("INSERT INTO videojuego_plataforma (videojuego_id, plataforma_id) VALUES (%s, %s)", relaciones)
            
            conn.commit()
            flash("Videojuego actualizado exitosamente.", "success")
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f"Error al editar: {e}", "error")
            
    cursor.execute("SELECT * FROM videojuegos WHERE id = %s", (id,))
    juego = cursor.fetchone()
    
    cursor.execute("SELECT id, nombre FROM desarrolladores ORDER BY nombre ASC")
    desarrolladores = cursor.fetchall()
    
    cursor.execute("SELECT id, nombre FROM plataformas ORDER BY nombre ASC")
    plataformas = cursor.fetchall()
    
    cursor.execute("SELECT plataforma_id FROM videojuego_plataforma WHERE videojuego_id=%s", (id,))
    juego_plats = [row['plataforma_id'] for row in cursor.fetchall()]
    
    conn.close()
    return render_template('edit_game.html', juego=juego, desarrolladores=desarrolladores, plataformas=plataformas, juego_plats=juego_plats)


@app.route('/admin/promote/<int:id>', methods=['POST'])
def promote_user(id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET is_admin = 1 WHERE id = %s", (id,))
        conn.commit()
        flash("Usuario ascendido a Administrador exitosamente.", "success")
    except Exception as e:
        flash(f"Error al ascender usuario: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_review/<int:game_id>/<int:review_id>', methods=['POST'])
def admin_delete_review(game_id, review_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # El admin no necesita comprobar si el usuario es el dueño de la review
        cursor.execute("DELETE FROM resenas WHERE id = %s AND videojuego_id = %s", (review_id, game_id))
        conn.commit()
        flash("Reseña moderada y eliminada por administrador.", "success")
    except Exception as e:
        flash(f"Error borrando la reseña: {e}", "error")
    finally:
        conn.close()
        
    return redirect(url_for('juego_detalle', id=game_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash("No se pudo conectar a la base de datos.", "error")
            return redirect(url_for('register'))
            
        cursor = conn.cursor(dictionary=True)
        
        # Verificar si usuario o correo ya existen
        cursor.execute("SELECT * FROM usuarios WHERE username = %s OR email = %s", (username, email))
        user_exists = cursor.fetchone()
        
        if user_exists:
            flash('El usuario o correo ya están registrados.', 'error')
        else:
            # Hash de la contraseña
            hashed_pw = generate_password_hash(password)
            try:
                cursor.execute("INSERT INTO usuarios (username, email, password_hash) VALUES (%s, %s, %s)",
                               (username, email, hashed_pw))
                conn.commit()
                flash('Te has registrado correctamente. Ahora puedes iniciar sesión.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error al registrar: {e}', 'error')
            finally:
                conn.close()
                
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash("No se pudo conectar a la base de datos.", "error")
            return redirect(url_for('login'))
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user.get('is_admin', 0) == 1
            flash(f'¡Bienvenido de nuevo, {user["username"]}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True, port=8080)