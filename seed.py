import mysql.connector
import locale

DB_HOST = 'roothosting.myddns.me'
DB_USER = 'root'
DB_PASSWORD = 'RootHosting_2021'
DB_NAME = 'flask-db'

def seed_database():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = connection.cursor(dictionary=True)
        
        # Check if we need to seed
        cursor.execute("SELECT COUNT(*) as count FROM videojuegos")
        count = cursor.fetchone()['count']
        
        if count == 0:
            print("Base de datos vacía, insertando datos de prueba...")
            
            # Desarrolladores
            desarrolladores = [
                ("CD Projekt Red", "Polonia"),
                ("Riot Games", "USA"),
                ("Rockstar Games", "USA"),
                ("Nintendo", "Japón")
            ]
            cursor.executemany("INSERT INTO desarrolladores (nombre, pais) VALUES (%s, %s)", desarrolladores)
            
            # Plataformas
            plataformas = [
                ("PC",), ("PlayStation 5",), ("Xbox Series X",), ("Nintendo Switch",)
            ]
            cursor.executemany("INSERT INTO plataformas (nombre) VALUES (%s)", plataformas)
            
            # Fetch inserted Data
            cursor.execute("SELECT id, nombre FROM desarrolladores")
            dev_map = {row['nombre']: row['id'] for row in cursor.fetchall()}
            
            cursor.execute("SELECT id, nombre FROM plataformas")
            plat_map = {row['nombre']: row['id'] for row in cursor.fetchall()}
            
            # Videojuegos
            juegos = [
                ("Cyber Strike 2077", dev_map["CD Projekt Red"]),
                ("League of Legends", dev_map["Riot Games"]),
                ("Red Dead Redemption II", dev_map["Rockstar Games"]),
                ("Super Mario Odyssey", dev_map["Nintendo"])
            ]
            cursor.executemany("INSERT INTO videojuegos (titulo, desarrollador_id) VALUES (%s, %s)", juegos)
            
            # Fetch Games
            cursor.execute("SELECT id, titulo FROM videojuegos")
            game_map = {row['titulo']: row['id'] for row in cursor.fetchall()}
            
            # Mapeo juego -> plataforma
            relaciones = [
                (game_map["Cyber Strike 2077"], plat_map["PC"]),
                (game_map["Cyber Strike 2077"], plat_map["PlayStation 5"]),
                (game_map["League of Legends"], plat_map["PC"]),
                (game_map["Red Dead Redemption II"], plat_map["PC"]),
                (game_map["Red Dead Redemption II"], plat_map["Xbox Series X"]),
                (game_map["Super Mario Odyssey"], plat_map["Nintendo Switch"])
            ]
            cursor.executemany("INSERT INTO videojuego_plataforma (videojuego_id, plataforma_id) VALUES (%s, %s)", relaciones)
            
            connection.commit()
            print("Semilla exitosa!")
        else:
            print(f"Juegos encontrados: {count}. No se ejecutará la semilla.")
            
    except Exception as e:
        print(f"Error seeding DB: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

if __name__ == '__main__':
    seed_database()
