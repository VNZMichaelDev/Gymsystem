# 🏗️ ARQUITECTURA DEL PROYECTO

## 📐 DIAGRAMA GENERAL

```
┌─────────────────────────────────────────────────────────────────┐
│                     USUARIO FINAL                               │
│                   (Navegador Web)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTPS (Railway)
                             │
        ┌────────────────────┴────────────────────┐
        │                                         │
        ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│   FRONTEND       │                    │   BACKEND        │
│  (HTML/JS/CSS)   │◄──────API REST────►│  (Flask)         │
│                  │                    │                  │
│ - index.html     │                    │ - /api/auth      │
│ - dashboard.html │                    │ - /api/clientes  │
│ - clientes.html  │                    │ - /api/pagos     │
│ - pagos.html     │                    │ - /api/membresias│
│ - reportes.html  │                    │ - /api/asistencia│
│ - etc.           │                    │ - /api/reportes  │
└──────────────────┘                    └────────┬─────────┘
                                                  │
                                    ┌─────────────┴─────────────┐
                                    │                           │
                                    ▼                           ▼
                            ┌──────────────┐         ┌──────────────────┐
                            │  PostgreSQL  │         │  File Storage    │
                            │  (Railway)   │         │  (/gym/uploads)  │
                            │              │         │                  │
                            │ - Usuarios   │         │ - Comprobantes   │
                            │ - Clientes   │         │ - Documentos     │
                            │ - Pagos      │         └──────────────────┘
                            │ - Membresías │
                            │ - Asistencias│
                            └──────────────┘
```

---

## 🗂️ ESTRUCTURA DE DIRECTORIOS

```
gym-system/
│
├── backend/                          # 🔧 API Flask
│   ├── app.py                        # Punto de entrada (create_app)
│   ├── config.py                     # Configuración (Config class)
│   ├── requirements.txt              # Dependencias Python
│   ├── Dockerfile                    # Para contenedores
│   ├── Procfile                      # Para Railway
│   │
│   └── gym/                          # Paquete principal
│       ├── __init__.py
│       ├── extensions.py             # BD, JWT, CORS
│       │
│       ├── models/                   # 📊 Modelos SQLAlchemy
│       │   ├── Usuario.py            # Usuarios (login)
│       │   ├── Cliente.py            # Clientes del gimnasio
│       │   ├── Membresia.py          # Tipos de membresías
│       │   ├── Pago.py               # Registro de pagos
│       │   └── Asistencia.py         # Control de asistencias
│       │
│       ├── blueprints/               # 🔌 Endpoints organizados
│       │   ├── auth/                 # Autenticación
│       │   │   └── views.py          # Login, logout, refresh
│       │   │
│       │   ├── clientes/             # CRUD Clientes
│       │   │   ├── crear.py          # POST /clientes
│       │   │   ├── views.py          # GET /clientes
│       │   │   ├── actualizar.py     # PUT /clientes/<id>
│       │   │   └── eliminar.py       # DELETE /clientes/<id>
│       │   │
│       │   ├── pagos/                # CRUD Pagos
│       │   │   ├── crear.py
│       │   │   ├── listar.py
│       │   │   ├── actualizar.py
│       │   │   ├── eliminar.py
│       │   │   └── descargar.py      # Descargar comprobantes
│       │   │
│       │   ├── membresias/           # CRUD Membresías
│       │   │   ├── crear.py
│       │   │   ├── listar.py
│       │   │   ├── actualizar.py
│       │   │   └── eliminar.py
│       │   │
│       │   ├── asistencia/           # CRUD Asistencias
│       │   │   ├── crear.py
│       │   │   ├── listar.py
│       │   │   ├── actualizar.py
│       │   │   └── eliminar.py
│       │   │
│       │   └── reportes/             # 📈 Reportes
│       │       ├── asistencias_por_cliente.py
│       │       ├── clientes_nuevos_por_mes.py
│       │       ├── ingresos_por_membresia.py
│       │       ├── membresias_activas.py
│       │       ├── pagos_pendientes.py
│       │       ├── pagos_por_mes.py
│       │       ├── retencion_clientes.py
│       │       ├── rentabilidad_clientes.py
│       │       ├── horarios_pico.py
│       │       ├── dashboard_ejecutivo.py
│       │       ├── membresias_por_vencer.py
│       │       ├── clientes_resumen.py
│       │       ├── pagos_resumen.py
│       │       ├── membresias_resumen.py
│       │       ├── asistencias_resumen.py
│       │       ├── asistencias_por_periodo.py
│       │       └── membresias_por_precio.py
│       │
│       ├── repositories/             # 🗄️ Acceso a datos
│       │   └── ...
│       │
│       ├── services/                 # 🔧 Lógica de negocio
│       │   └── ...
│       │
│       ├── utils/                    # 🛠️ Funciones auxiliares
│       │   └── ...
│       │
│       ├── uploads/                  # 📁 Archivos subidos
│       │   └── (comprobantes de pago)
│       │
│       └── bd/                       # 🗄️ Base de datos local
│           └── base_Datos.db         # SQLite (desarrollo)
│
├── frontend/                         # 🎨 Interfaz web
│   ├── index.html                    # 🔐 Login
│   ├── dashboard.html                # 📊 Dashboard principal
│   ├── clientes.html                 # 👥 Gestión de clientes
│   ├── membresias.html               # 💳 Gestión de membresías
│   ├── pagos.html                    # 💰 Gestión de pagos
│   ├── asistencia.html               # ✅ Control de asistencias
│   ├── reportes.html                 # 📈 Reportes
│   ├── reset-password.html           # 🔑 Recuperar contraseña
│   ├── debug-pagos.html              # 🐛 Debug
│   │
│   ├── assets/                       # 🎨 Recursos
│   │   ├── css/                      # Estilos
│   │   ├── images/                   # Imágenes
│   │   └── fonts/                    # Fuentes
│   │
│   └── js/                           # 📜 JavaScript
│       ├── api.js                    # Funciones de API
│       ├── auth.js                   # Autenticación
│       └── ...
│
├── .env.example                      # 📝 Template de variables
├── .gitignore                        # 🚫 Archivos ignorados
├── Procfile                          # 🚀 Comando para Railway
│
├── ANALISIS_PROYECTO.md              # 📊 Análisis completo
├── ARQUITECTURA.md                   # 🏗️ Este archivo
├── COMANDOS_DESPLIEGUE.md            # 🔧 Comandos listos
├── DESPLIEGUE_RAILWAY_RAPIDO.md      # ⚡ Guía rápida
├── RAILWAY_DEPLOYMENT_GUIDE.md       # 📚 Guía detallada
└── STATUS.md                         # ✅ Estado del proyecto
```

---

## 🔄 FLUJO DE DATOS

### 1. Autenticación
```
Usuario escribe credenciales
        ↓
Frontend envía POST /api/auth/login
        ↓
Backend valida contraseña (bcrypt)
        ↓
Backend genera JWT token
        ↓
Frontend guarda token en localStorage
        ↓
Frontend incluye token en headers Authorization
```

### 2. Crear Cliente
```
Usuario completa formulario
        ↓
Frontend valida datos
        ↓
Frontend envía POST /api/clientes
        ↓
Backend valida datos nuevamente
        ↓
Backend crea registro en BD
        ↓
Backend retorna cliente creado
        ↓
Frontend actualiza tabla
```

### 3. Registrar Pago
```
Usuario sube comprobante
        ↓
Frontend valida archivo (Pillow)
        ↓
Frontend envía POST /api/pagos con archivo
        ↓
Backend valida tipo MIME (python-magic)
        ↓
Backend guarda archivo en /gym/uploads
        ↓
Backend crea registro de pago en BD
        ↓
Backend retorna confirmación
        ↓
Frontend muestra éxito
```

### 4. Generar Reporte
```
Usuario selecciona filtros
        ↓
Frontend envía GET /api/reportes/...
        ↓
Backend consulta BD con filtros
        ↓
Backend procesa datos
        ↓
Backend retorna JSON
        ↓
Frontend renderiza gráfico
```

---

## 🗄️ MODELO DE DATOS

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO                                  │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ email (UNIQUE)                                                  │
│ password_hash (bcrypt)                                          │
│ nombre_completo                                                 │
│ rol (admin, gerente, recepcionista)                            │
│ is_active                                                       │
│ created_at, updated_at                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1:N
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE                                  │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ nombre_completo                                                 │
│ email                                                           │
│ telefono                                                        │
│ dni/ce/ruc                                                      │
│ fecha_nacimiento                                                │
│ direccion                                                       │
│ created_at, updated_at                                          │
└─────────────────────────────────────────────────────────────────┘
        │                               │
        │ 1:N                           │ 1:N
        ▼                               ▼
┌──────────────────────┐      ┌──────────────────────┐
│    MEMBRESIA         │      │      PAGO            │
├──────────────────────┤      ├──────────────────────┤
│ id (PK)              │      │ id (PK)              │
│ cliente_id (FK)      │      │ cliente_id (FK)      │
│ tipo_membresia       │      │ membresia_id (FK)    │
│ fecha_inicio         │      │ monto                │
│ fecha_vencimiento    │      │ metodo_pago          │
│ precio               │      │ comprobante_path     │
│ estado (activa...)   │      │ estado (pendiente...) │
│ created_at, updated_at      │ created_at, updated_at
└──────────────────────┘      └──────────────────────┘
        │
        │ 1:N
        ▼
┌──────────────────────┐
│    ASISTENCIA        │
├──────────────────────┤
│ id (PK)              │
│ cliente_id (FK)      │
│ fecha_hora           │
│ tipo (entrada/salida)│
│ created_at, updated_at
└──────────────────────┘
```

---

## 🔌 API ENDPOINTS

### Autenticación
```
POST   /api/auth/login              # Login
POST   /api/auth/logout             # Logout
POST   /api/auth/refresh            # Refresh token
POST   /api/auth/reset-password     # Recuperar contraseña
```

### Clientes
```
POST   /api/clientes                # Crear cliente
GET    /api/clientes                # Listar clientes
GET    /api/clientes/<id>           # Obtener cliente
PUT    /api/clientes/<id>           # Actualizar cliente
DELETE /api/clientes/<id>           # Eliminar cliente
```

### Membresías
```
POST   /api/membresias              # Crear membresía
GET    /api/membresias              # Listar membresías
GET    /api/membresias/<id>         # Obtener membresía
PUT    /api/membresias/<id>         # Actualizar membresía
DELETE /api/membresias/<id>         # Eliminar membresía
```

### Pagos
```
POST   /api/pagos                   # Crear pago
GET    /api/pagos                   # Listar pagos
GET    /api/pagos/<id>              # Obtener pago
PUT    /api/pagos/<id>              # Actualizar pago
DELETE /api/pagos/<id>              # Eliminar pago
GET    /api/pagos/<id>/descargar    # Descargar comprobante
```

### Asistencias
```
POST   /api/asistencias             # Registrar asistencia
GET    /api/asistencias             # Listar asistencias
GET    /api/asistencias/<id>        # Obtener asistencia
PUT    /api/asistencias/<id>        # Actualizar asistencia
DELETE /api/asistencias/<id>        # Eliminar asistencia
```

### Reportes
```
GET    /api/reportes/asistencias-por-cliente
GET    /api/reportes/clientes-nuevos-por-mes
GET    /api/reportes/ingresos-por-membresia
GET    /api/reportes/membresias-activas
GET    /api/reportes/pagos-pendientes
GET    /api/reportes/pagos-por-mes
GET    /api/reportes/retencion-clientes
GET    /api/reportes/rentabilidad-clientes
GET    /api/reportes/horarios-pico
GET    /api/reportes/dashboard-ejecutivo
GET    /api/reportes/membresias-por-vencer
GET    /api/reportes/clientes-resumen
GET    /api/reportes/pagos-resumen
GET    /api/reportes/membresias-resumen
GET    /api/reportes/asistencias-resumen
GET    /api/reportes/asistencias-por-periodo
GET    /api/reportes/membresias-por-precio
```

### Health Check
```
GET    /api/health                  # Estado de la API
```

---

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

```
┌─────────────────────────────────────────┐
│     Usuario intenta acceder             │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ ¿Tiene JWT token?  │
        └────────┬───────────┘
                 │
        ┌────────┴────────┐
        │                 │
       NO                YES
        │                 │
        ▼                 ▼
    401 Unauthorized  ┌─────────────────┐
                      │ ¿Token válido?  │
                      └────────┬────────┘
                               │
                       ┌───────┴────────┐
                       │                │
                      NO               YES
                       │                │
                       ▼                ▼
                  401 Invalid       ┌──────────────┐
                                    │ ¿Token exp?  │
                                    └────────┬─────┘
                                             │
                                     ┌───────┴────────┐
                                     │                │
                                    YES              NO
                                     │                │
                                     ▼                ▼
                                401 Expired      ✅ Permitir
                                                 acceso
```

---

## 📦 DEPENDENCIAS PRINCIPALES

```
Flask                    # Framework web
Flask-CORS              # CORS
Flask-Migrate           # Migraciones
SQLAlchemy              # ORM
flask-jwt-extended      # JWT
bcrypt                  # Hashing
python-dotenv           # Variables de entorno
Pillow                  # Imágenes
APScheduler             # Tareas programadas
pytest                  # Testing
```

---

## 🚀 DESPLIEGUE EN RAILWAY

```
┌──────────────────────────────────────────────────────────────┐
│                    RAILWAY PLATFORM                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │   WEB SERVICE    │         │   DATABASE       │          │
│  │  (Flask App)     │◄───────►│  (PostgreSQL)    │          │
│  │                  │         │                  │          │
│  │ - Python 3.11    │         │ - Automático     │          │
│  │ - Port 5000      │         │ - DATABASE_URL   │          │
│  │ - Auto-deploy    │         │ - Backups        │          │
│  └──────────────────┘         └──────────────────┘          │
│         │                                                    │
│         │ Conectado a GitHub                                │
│         │ (Auto-redeploy en push)                           │
│         │                                                    │
│  ┌──────▼──────────────────────────────────────────┐        │
│  │         GITHUB REPOSITORY                       │        │
│  │  (gym-system)                                   │        │
│  │  - backend/                                     │        │
│  │  - frontend/                                    │        │
│  │  - Procfile                                     │        │
│  └─────────────────────────────────────────────────┘        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🎯 FLUJO DE DESPLIEGUE

```
1. Push a GitHub
        ↓
2. Railway detecta cambios
        ↓
3. Railway ejecuta Build Command
   pip install -r backend/requirements.txt
        ↓
4. Railway ejecuta Start Command
   cd backend && python app.py
        ↓
5. Flask inicia en puerto 5000
        ↓
6. Railway expone en https://tu-app.railway.app
        ↓
7. Frontend accede a API en /api/...
        ↓
8. ✅ App en vivo
```

---

## 📊 RESUMEN TÉCNICO

| Aspecto | Tecnología |
|---------|-----------|
| Backend | Flask 2.x |
| ORM | SQLAlchemy |
| Base de datos | PostgreSQL (Railway) |
| Autenticación | JWT |
| Hashing | bcrypt |
| Frontend | HTML5/CSS3/JavaScript |
| Despliegue | Railway |
| Contenedores | Docker |
| CI/CD | GitHub Actions (opcional) |

---

**Arquitectura lista para producción** ✅
