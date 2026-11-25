CREATE DATABASE IF NOT EXISTS muni_yau_db;
USE muni_yau_db;

CREATE TABLE ciudadanos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dni VARCHAR(15) NOT NULL UNIQUE,
    nombre_completo VARCHAR(120) NOT NULL,
    correo VARCHAR(120),
    telefono VARCHAR(25)
);

CREATE TABLE tramites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ciudadano_id INT NOT NULL,
    tipo_tramite VARCHAR(100) NOT NULL,
    area_asignada VARCHAR(100) NOT NULL,
    documentos_completos TINYINT(1) DEFAULT 0,
    estado VARCHAR(40) DEFAULT 'Pendiente',
    prioridad_ml VARCHAR(20) DEFAULT 'Media',
    score_urgencia DECIMAL(5,2) DEFAULT 0.00,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ciudadano_id) REFERENCES ciudadanos(id)
);

CREATE TABLE historial_notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tramite_id INT NOT NULL,
    canal VARCHAR(30) NOT NULL,
    mensaje TEXT NOT NULL,
    enviado_en DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tramite_id) REFERENCES tramites(id)
);