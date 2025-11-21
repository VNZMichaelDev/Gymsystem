# 🏋️ GET FIT — Gym Management System

Sistema completo de gestión de gimnasios con backend Flask + frontend HTML/JS.

## ✨ Características

- ✅ **Gestión de clientes** - CRUD completo con validación
- ✅ **Membresías** - Tipos, precios, vencimientos
- ✅ **Pagos** - Registro con comprobantes, validación de archivos
- ✅ **Asistencias** - Control de entrada/salida
- ✅ **Reportes** - 12+ reportes analíticos
- ✅ **Autenticación** - JWT con roles de usuario
- ✅ **API REST** - 40+ endpoints
- ✅ **Responsive** - Interfaz adaptable a móviles

## 📁 Estructura

```
gym-system/
├── backend/          # Flask API
├── frontend/         # HTML/JS/CSS
├── Procfile          # Para Railway
├── .env.example      # Variables de entorno
└── [Guías de despliegue]
```

## 🚀 Despliegue en Railway (RECOMENDADO)

**Estado**: ✅ **LISTO PARA DESPLEGAR**

### Pasos rápidos (15 minutos)

1. **Preparar**:
```bash
cd backend
copy ..\\.env.example .env
# Editar .env con claves secretas
```

2. **GitHub**:
```bash
cd ..
git init
git add .
git commit -m "Ready for Railway"
git remote add origin https://github.com/tu-usuario/get-fit.git
git push -u origin main
```

3. **Railway**:
- Ir a https://railway.app
- Conectar GitHub repo
- Agregar PostgreSQL
- Configurar variables de entorno
- ¡Listo!

**Costo**: $0 USD/mes (5 USD crédito gratuito)

## 💻 Ejecutar localmente

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Luego abrir: `http://localhost:5000`

## 📚 Documentación

| Archivo | Propósito |
|---------|-----------|
| **DESPLIEGUE_RAILWAY_RAPIDO.md** | ⚡ Guía rápida (5 min) |
| **RAILWAY_DEPLOYMENT_GUIDE.md** | 📖 Guía detallada |
| **ANALISIS_PROYECTO.md** | 📊 Análisis técnico |
| **ARQUITECTURA.md** | 🏗️ Diagrama de arquitectura |
| **COMANDOS_DESPLIEGUE.md** | 🔧 Comandos listos para copiar |
| **STATUS.md** | ✅ Estado actual |

## 🔐 Seguridad

- ✅ Autenticación JWT
- ✅ Hashing bcrypt para contraseñas
- ✅ CORS configurable
- ✅ Validación de entrada
- ✅ Variables de entorno para secretos

## 📊 API Endpoints

```
POST   /api/auth/login              # Login
GET    /api/clientes                # Listar clientes
POST   /api/pagos                   # Crear pago
GET    /api/reportes/...            # Reportes
... y más (40+ endpoints)
```

## 🛠️ Stack Técnico

- **Backend**: Flask, SQLAlchemy, JWT
- **Frontend**: HTML5, CSS3, JavaScript
- **BD**: PostgreSQL (Railway) / SQLite (local)
- **Deploy**: Railway
- **Contenedores**: Docker

## 📋 Requisitos

- Python 3.10+
- Git
- Cuenta GitHub (para despliegue)
- Cuenta Railway (gratis)

## 🎯 Próximos pasos

1. Leer `DESPLIEGUE_RAILWAY_RAPIDO.md`
2. Crear `.env` en `backend/`
3. Subir a GitHub
4. Desplegar en Railway

## 📞 Soporte

- Revisar guías de despliegue
- Ver logs: `railway logs`
- Documentación: https://docs.railway.app

---

**Estado**: ✅ Listo para producción  
**Última actualización**: Hoy  
**Tiempo de despliegue**: 15-20 minutos
