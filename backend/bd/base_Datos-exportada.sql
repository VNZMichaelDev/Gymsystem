BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS Asistencia (
    id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    fecha TEXT NOT NULL,
    hora_entrada TEXT NOT NULL,
    hora_salida TEXT,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);
CREATE TABLE IF NOT EXISTS Clientes (
    id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_documento TEXT NOT NULL,
    numero_documento TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    apellido_paterno TEXT NOT NULL,
    apellido_materno TEXT NOT NULL,
    correo TEXT,
    telefono TEXT,
    fecha_registro TEXT NOT NULL,
    id_membresia INTEGER,
    FOREIGN KEY (id_membresia) REFERENCES Membresias(id_membresia)
);
CREATE TABLE IF NOT EXISTS Membresias (
    id_membresia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    duracion_dias INTEGER NOT NULL,
    precio REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS Pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_membresia INTEGER NOT NULL,
    fecha_pago TEXT NOT NULL,
    fecha_inicio_membresia TEXT NOT NULL,
    fecha_fin_membresia TEXT NOT NULL,
    monto_total REAL NOT NULL,
    monto_pagado REAL NOT NULL,
    monto_pendiente REAL NOT NULL DEFAULT 0.0,
    comprobante TEXT,
    estado TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_membresia) REFERENCES Membresias(id_membresia)
);
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    fecha_creacion TEXT NOT NULL
, reset_token TEXT, reset_token_expires TEXT);
CREATE TABLE IF NOT EXISTS "_alembic_tmp_Asistencia" (
	id_asistencia INTEGER NOT NULL, 
	id_cliente INTEGER NOT NULL, 
	fecha VARCHAR(32) NOT NULL, 
	hora_entrada VARCHAR(8) NOT NULL, 
	hora_salida VARCHAR(8), 
	PRIMARY KEY (id_asistencia), 
	FOREIGN KEY(id_cliente) REFERENCES "Clientes" (id_cliente)
);
CREATE TABLE IF NOT EXISTS alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO "Asistencia" ("id_asistencia","id_cliente","fecha","hora_entrada","hora_salida") VALUES (1,1,'2025-09-15','07:15','20:09'),
 (2,1,'2025-09-17','18:10','19:05'),
 (3,1,'2025-09-22','07:05','08:10'),
 (4,1,'2025-10-01','07:12','08:20'),
 (5,2,'2025-09-13','19:20','20:10'),
 (6,2,'2025-09-18','06:55','07:50'),
 (7,2,'2025-09-25','19:05','20:00'),
 (8,3,'2025-09-16','08:00','09:00'),
 (9,3,'2025-09-19','08:05','09:05'),
 (10,3,'2025-09-26','18:30','19:20'),
 (11,4,'2025-09-02','06:50','07:40'),
 (12,4,'2025-09-09','06:55','07:50'),
 (13,4,'2025-09-23','06:48','07:45'),
 (14,5,'2025-09-06','20:10','21:00'),
 (15,5,'2025-09-11','20:05','20:55'),
 (16,5,'2025-09-27','09:15','10:05'),
 (17,6,'2025-09-03','07:30','08:20'),
 (18,6,'2025-09-10','07:28','08:25'),
 (19,6,'2025-09-24','19:00','19:50'),
 (20,1,'2025-10-03','18:09','20:30'),
 (21,11,'2025-10-04','21:11','21:11:09'),
 (22,11,'2025-10-04','21:11','21:11:35'),
 (23,1,'2025-10-04','21:13','21:13:38'),
 (24,11,'2025-10-04','21:16','21:16:06'),
 (25,8,'2025-10-05','19:09','19:09:07'),
 (26,8,'2025-10-05','19:37','19:37'),
 (28,9,'2025-10-05','19:38','19:39'),
 (30,1,'2025-10-05','19:38','19:39'),
 (31,5,'2025-10-05','19:42','10:33'),
 (32,3,'2025-10-05','19:42','10:33'),
 (33,NULL,'2025-10-05','21:28','10:32'),
 (34,2,'2025-10-06','10:32','10:32'),
 (35,8,'2025-10-06','10:33','10:33'),
 (36,8,'2025-10-07','11:16','11:16');
INSERT INTO "Clientes" ("id_cliente","tipo_documento","numero_documento","nombre","apellido_paterno","apellido_materno","correo","telefono","fecha_registro","id_membresia") VALUES (1,'DNI','72839410','Juan Carlos','Ramos','Vega','juan.ramos@example.com','987654321','2025-09-10',8),
 (2,'DNI','45678912','MarÃ­a Fernanda','ALENADRIA','Ruiz','maria.torres@example.com','966112233','2025-09-12',2),
 (3,'CE','X12345678','Ana Sofia','Muller','-','ana.muller@example.com','955998877','2025-09-14',2),
 (4,'RUC','10456789123','Luis Alberto','Paredes','Ochoa','luis.paredes@example.com','944223344','2025-08-20',3),
 (5,'DNI','11223344','Pedro Miguel','Salazar','Lujan','pedro.salazar@example.com','933445566','2025-09-05',1),
 (6,'DNI','99887766','Karina Paola','Espinoza','Cueva','karina.espinoza@example.com','922556677','2025-07-01',NULL),
 (8,'DNI','12345678','Juan','ORTIZ','CASTILLO','juan.perez@email.com','987654321','2025-10-04',5),
 (9,'DNI','87654321','María','García','López','maria.garcia@email.com','123456789','2025-10-04',8),
 (10,'CE','CE123456','Carlos','Rodríguez','Martín','carlos.rodriguez@email.com','456789123','2025-10-04',9),
 (11,'DNI','44332211','Luis','Martínez','Silva','luis.martinez@email.com','321654987','2025-10-04',2),
 (16,'DNI','7023243','piero-gym','RUIZ','VALDEZ','ruizruizpiero2@gmail.com','f010119992','2025-10-06',NULL),
 (17,'DNI','71089478','cristobal','ruiz','castillo','rpieroalexandro@gmail.com','','2025-10-06',12);
INSERT INTO "Membresias" ("id_membresia","nombre","duracion_dias","precio") VALUES (1,'Mensual Basica',30,80.0),
 (2,'Mensual Full',30,120.0),
 (3,'Trimestral',90,300.0),
 (5,'cuatrimestre',120,240.0),
 (6,'Básica',30,50.0),
 (7,'Premium',30,80.0),
 (8,'VIP',30,120.0),
 (9,'Anual Básica',365,500.0),
 (10,'año pendejo',365,800.0),
 (12,'promo-3 meses',90,250.0),
 (13,'Anual Premium',365,800.0),
 (14,'diaria',1,5.0);
INSERT INTO "Pagos" ("id_pago","id_cliente","id_membresia","fecha_pago","fecha_inicio_membresia","fecha_fin_membresia","monto_total","monto_pagado","monto_pendiente","comprobante","estado") VALUES (1,2,1,'2025-10-07','2025-10-07','2025-11-06',150.0,50.0,70.0,NULL,'Pendiente'),
 (3,1,8,'2025-10-07','2025-10-07','2025-11-06',120.0,100.0,20.0,'gym/uploads/comprobantes\5a908d27fcef4022ae39d53dfef43b61.png','Pendiente'),
 (4,1,8,'2025-10-07','2025-10-07','2025-11-06',120.0,20.0,0.0,'gym/uploads/comprobantes\9440a281e3fc4807805b537041a84fcb.png','Pagado'),
 (5,2,2,'2025-10-07','2025-10-07','2025-11-06',120.0,70.0,0.0,NULL,'Pagado');
INSERT INTO "Usuarios" ("id_usuario","correo","contrasena_hash","fecha_creacion","reset_token","reset_token_expires") VALUES (1,'admin@gym.local','scrypt:32768:8:1$2xiEQrUAhind6dNp$7237f304279f98af140d93884065ef1e5ea225e041ef11d6ecd00e047c46b7a62a010d5b3be34325c98d45c00d4dd455d2ddde717bdbdf2b0048726bc1c30fbf','2025-10-01 12:00:00',NULL,NULL),
 (2,'admin@gym.com','$2b$12$/N//.F6x2qerjihgsv/tkeVLbe6eIf9LGjuNpwEtN/m8xu1YMbm2.','2025-10-04 19:32:27',NULL,NULL);
INSERT INTO "alembic_version" ("version_num") VALUES ('3ef69d678b68');
COMMIT;
