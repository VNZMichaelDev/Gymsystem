-- Eliminar tablas existentes (en orden correcto para evitar conflictos de FK)
DROP TABLE IF EXISTS Asistencia;
DROP TABLE IF EXISTS Pagos;
DROP TABLE IF EXISTS Clientes;
DROP TABLE IF EXISTS Membresias;
DROP TABLE IF EXISTS Usuarios;

-- Creación de la tabla Usuarios (Control de acceso)
CREATE TABLE Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    correo TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    fecha_creacion TEXT NOT NULL
);

-- Creación de la tabla Membresías
CREATE TABLE Membresias (
    id_membresia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    duracion_dias INTEGER NOT NULL,
    precio REAL NOT NULL
);

-- Creación de la tabla Clientes
CREATE TABLE Clientes (
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

-- Creación de la tabla Pagos
CREATE TABLE Pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    fecha_pago TEXT NOT NULL,
    monto REAL NOT NULL,
    comprobante TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);

-- Creación de la tabla Asistencia
CREATE TABLE Asistencia (
    id_asistencia INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER,
    fecha TEXT NOT NULL,
    hora_entrada TEXT NOT NULL,
    hora_salida TEXT,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);


PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

-- ======================
-- 1) Membresías
-- ======================
INSERT INTO Membresias (nombre, duracion_dias, precio) VALUES
  ('Mensual Básica', 30, 80.00),
  ('Mensual Full',   30, 120.00),
  ('Trimestral',     90, 300.00),
  ('Anual',         365, 1000.00);

-- ======================
-- 2) Usuario (acceso único)
--    Nota: "contraseña_hash" es un hash de ejemplo (reemplázalo por el tuyo)
-- ======================
INSERT INTO Usuarios (correo, contrasena_hash, fecha_creacion) VALUES
  ('admin@gym.local', '$2b$12$KIXQ4o9dtp8hGIa6N4GzOeJYxZ5p2M0a9eG6P7v3cQeXW8rY1Zk0e', '2025-10-01 12:00:00');

-- ======================
-- 3) Clientes
--    (Se asume que los IDs de membresía quedaron: 1=Mensual Básica, 2=Mensual Full, 3=Trimestral, 4=Anual)
-- ======================
INSERT INTO Clientes (tipo_documento, numero_documento, nombre, apellido_paterno, apellido_materno, correo, telefono, fecha_registro, id_membresia) VALUES
  ('DNI', '72839410', 'Juan Carlos',  'Ramos',   'Vega',   'juan.ramos@example.com',  '987654321', '2025-09-10', 1),
  ('DNI', '45678912', 'María Fernanda','Torres', 'Ruiz',   'maria.torres@example.com','966112233', '2025-09-12', 2),
  ('CE',  'X12345678','Ana Sofia',    'Muller',  '-',      'ana.muller@example.com',  '955998877', '2025-09-14', 2),
  ('RUC', '10456789123','Luis Alberto','Paredes','Ochoa',  'luis.paredes@example.com','944223344', '2025-08-20', 3),
  ('DNI', '11223344', 'Pedro Miguel', 'Salazar', 'Lujan',  'pedro.salazar@example.com','933445566','2025-09-05', 1),
  ('DNI', '99887766', 'Karina Paola', 'Espinoza','Cueva',  'karina.espinoza@example.com','922556677','2025-07-01',4);

-- ======================
-- 4) Pagos (comprobantes como rutas de imagen)
-- ======================
INSERT INTO Pagos (id_cliente, fecha_pago, monto, comprobante, estado) VALUES
  (1, '2025-09-10',  80.00,  'uploads/comprobantes/2025-09-10_72839410.jpg', 'Confirmado'),
  (1, '2025-10-01',  80.00,  'uploads/comprobantes/2025-10-01_72839410.jpg', 'Confirmado'),
  (2, '2025-09-12', 120.00,  'uploads/comprobantes/2025-09-12_45678912.jpg', 'Confirmado'),
  (2, '2025-10-01', 120.00,  'uploads/comprobantes/2025-10-01_45678912.jpg', 'Pendiente'),
  (3, '2025-09-14', 120.00,  'uploads/comprobantes/2025-09-14_X12345678.jpg', 'Confirmado'),
  (4, '2025-08-20', 300.00,  'uploads/comprobantes/2025-08-20_10456789123.jpg', 'Confirmado'),
  (5, '2025-09-05',  80.00,  'uploads/comprobantes/2025-09-05_11223344.jpg', 'Confirmado'),
  (6, '2025-07-01',1000.00,  'uploads/comprobantes/2025-07-01_99887766.jpg', 'Confirmado'),
  (4, '2025-09-20',  0.00,   'uploads/comprobantes/2025-09-20_10456789123.jpg', 'Pendiente'), -- renovación futura (ejemplo)
  (3, '2025-10-01', 120.00,  'uploads/comprobantes/2025-10-01_X12345678.jpg', 'Pendiente');

-- ======================
-- 5) Asistencia (septiembre–octubre 2025)
-- ======================
INSERT INTO Asistencia (id_cliente, fecha, hora_entrada, hora_salida) VALUES
  -- Juan Carlos (1)
  (1, '2025-09-15', '07:15', '08:30'),
  (1, '2025-09-17', '18:10', '19:05'),
  (1, '2025-09-22', '07:05', '08:10'),
  (1, '2025-10-01', '07:12', '08:20'),
  -- María Fernanda (2)
  (2, '2025-09-13', '19:20', '20:10'),
  (2, '2025-09-18', '06:55', '07:50'),
  (2, '2025-09-25', '19:05', '20:00'),
  -- Ana Sofia (3)
  (3, '2025-09-16', '08:00', '09:00'),
  (3, '2025-09-19', '08:05', '09:05'),
  (3, '2025-09-26', '18:30', '19:20'),
  -- Luis Alberto (4)
  (4, '2025-09-02', '06:50', '07:40'),
  (4, '2025-09-09', '06:55', '07:50'),
  (4, '2025-09-23', '06:48', '07:45'),
  -- Pedro Miguel (5)
  (5, '2025-09-06', '20:10', '21:00'),
  (5, '2025-09-11', '20:05', '20:55'),
  (5, '2025-09-27', '09:15', '10:05'),
  -- Karina Paola (6)
  (6, '2025-09-03', '07:30', '08:20'),
  (6, '2025-09-10', '07:28', '08:25'),
  (6, '2025-09-24', '19:00', '19:50');

COMMIT;