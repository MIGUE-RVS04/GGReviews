import mysql.connector

try:
    conn = mysql.connector.connect(host='roothosting.myddns.me', user='root', password='RootHosting_2021', database='flask-db')
    cursor = conn.cursor()
    # Intenta agregar la columna
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("Columna agregada exitosamente.")
    except Exception as e:
        print(f"Nota (no es un error grave): {e}")

    # Promueve al primer usuario que se haya registrado
    cursor.execute("UPDATE usuarios SET is_admin = 1 ORDER BY id ASC LIMIT 1")
    conn.commit()
    print("Primer usuario promovido a admin.")
    conn.close()
except Exception as e:
    print(f"Error fatal: {e}")
