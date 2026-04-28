CREATE TABLE desarrolladores (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    pais VARCHAR(50),
    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE usuarios (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

CREATE TABLE plataformas (
    id INT NOT NULL AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB;

-- 3. Crear tablas con llaves foráneas simples
CREATE TABLE videojuegos (
    id INT NOT NULL AUTO_INCREMENT,
    titulo VARCHAR(150) NOT NULL,
    desarrollador_id INT,
    PRIMARY KEY (id),
    CONSTRAINT fk_vid_desarrollador 
        FOREIGN KEY (desarrollador_id) REFERENCES desarrolladores(id) 
        ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. Crear tablas de relación (Las que suelen dar el error 150)
CREATE TABLE videojuego_plataforma (
    videojuego_id INT NOT NULL,
    plataforma_id INT NOT NULL,
    PRIMARY KEY (videojuego_id, plataforma_id),
    CONSTRAINT fk_vp_videojuego 
        FOREIGN KEY (videojuego_id) REFERENCES videojuegos(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_vp_plataforma 
        FOREIGN KEY (plataforma_id) REFERENCES plataformas(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE resenas (
    id INT NOT NULL AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    videojuego_id INT NOT NULL,
    calificacion INT NOT NULL,
    comentario TEXT,
    PRIMARY KEY (id),
    CONSTRAINT fk_res_usuario 
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_res_videojuego 
        FOREIGN KEY (videojuego_id) REFERENCES videojuegos(id) 
        ON DELETE CASCADE
) ENGINE=InnoDB;