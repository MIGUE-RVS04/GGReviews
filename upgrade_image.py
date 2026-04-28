import mysql.connector

try:
    conn = mysql.connector.connect(host='roothosting.myddns.me', user='root', password='RootHosting_2021', database='flask-db')
    cursor = conn.cursor()
    # Intenta agregar la columna
    try:
        cursor.execute("ALTER TABLE videojuegos ADD COLUMN imagen_url VARCHAR(500) DEFAULT ''")
        conn.commit()
        print("Columna 'imagen_url' agregada a videojuegos exitosamente.")
    except Exception as e:
        print(f"Nota (no es un error grave): {e}")

    conn.close()
except Exception as e:
    print(f"Error fatal: {e}")
