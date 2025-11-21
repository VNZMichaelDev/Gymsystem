# 🔧 COMANDOS LISTOS PARA COPIAR Y PEGAR

## 1️⃣ PREPARAR LOCALMENTE

### Crear archivo .env
```bash
cd backend
copy ..\\.env.example .env
```

Luego editar `.env` y cambiar:
```
SECRET_KEY=tu-clave-aleatoria-aqui-32-caracteres-minimo
JWT_SECRET_KEY=tu-jwt-secret-aqui-32-caracteres-minimo
```

### Probar localmente (opcional)
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Luego abrir: `http://localhost:5000`

---

## 2️⃣ SUBIR A GITHUB

### Opción A: Desde PowerShell (Windows)

```powershell
# Ir a la carpeta del proyecto
cd C:\Users\ElixirStudio\Desktop\get-fit-main\get-fit-main\gym-system

# Inicializar git
git init
git config user.name "Tu Nombre"
git config user.email "tu@email.com"

# Agregar todos los archivos
git add .

# Commit
git commit -m "Gym system ready for Railway deployment"

# Crear rama main
git branch -M main

# Agregar remoto (reemplazar TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/get-fit.git

# Push
git push -u origin main
```

### Opción B: Crear repo en GitHub primero

1. Ir a https://github.com/new
2. Nombre: `get-fit`
3. Descripción: `Gym Management System`
4. Público
5. Crear repo
6. Copiar URL (ej: `https://github.com/tu-usuario/get-fit.git`)
7. Ejecutar:

```powershell
cd C:\Users\ElixirStudio\Desktop\get-fit-main\get-fit-main\gym-system
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <PEGAR_URL_AQUI>
git push -u origin main
```

---

## 3️⃣ DESPLEGAR EN RAILWAY

### Opción A: Desde Railway Web UI (Recomendado)

1. Ir a https://railway.app
2. Hacer clic en **"Start a New Project"**
3. Seleccionar **"Deploy from GitHub"**
4. Autorizar GitHub si es necesario
5. Seleccionar repo `get-fit`
6. Railway detectará automáticamente que es Python

### Opción B: Usar Railway CLI

```bash
# Instalar Railway CLI (si no lo tienes)
npm install -g @railway/cli

# Login
railway login

# Ir a la carpeta del proyecto
cd C:\Users\ElixirStudio\Desktop\get-fit-main\get-fit-main\gym-system

# Inicializar proyecto en Railway
railway init

# Desplegar
railway up
```

---

## 4️⃣ CONFIGURAR EN RAILWAY

### Agregar PostgreSQL

```bash
# Desde Railway CLI
railway add

# Seleccionar "Database" → "PostgreSQL"
# Railway crea automáticamente DATABASE_URL
```

O desde web UI:
1. En el proyecto, click **"+ Add Service"**
2. Seleccionar **"Database"** → **"PostgreSQL"**

### Configurar Variables de Entorno

Desde web UI:
1. Ir a servicio web → **"Variables"**
2. Agregar:

```
FLASK_ENV=production
SECRET_KEY=generar-clave-aleatoria-aqui
JWT_SECRET_KEY=generar-clave-aleatoria-aqui
CORS_ORIGINS=https://tu-app.railway.app
```

O desde CLI:
```bash
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=tu-clave-aqui
railway variables set JWT_SECRET_KEY=tu-jwt-secret-aqui
railway variables set CORS_ORIGINS=https://tu-app.railway.app
```

### Configurar Build & Deploy

Desde web UI:
1. Ir a servicio web → **"Settings"**
2. Build Command:
```
pip install -r backend/requirements.txt
```

3. Start Command:
```
cd backend && python app.py
```

4. Port: `5000`

---

## 5️⃣ VERIFICAR DESPLIEGUE

### Ver logs
```bash
railway logs
```

### Ver URL pública
```bash
railway open
```

### Probar API
```bash
# Reemplazar con tu URL de Railway
curl https://tu-app.railway.app/api/health
```

Debería responder:
```json
{"status": "ok"}
```

---

## 🐛 SOLUCIONAR PROBLEMAS

### Error: "ModuleNotFoundError: No module named 'gym'"

**Solución 1**: Cambiar Start Command a:
```
cd backend && PYTHONPATH=/app/backend python app.py
```

**Solución 2**: Cambiar Build Command a:
```
cd backend && pip install -r requirements.txt
```

### Error: "No such file or directory: 'frontend'"

Verificar estructura en GitHub:
```
gym-system/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── gym/
├── frontend/
│   ├── index.html
│   └── ...
└── Procfile
```

Si no está así, hacer push nuevamente:
```bash
git add .
git commit -m "Fix directory structure"
git push
```

### Error: "Database connection failed"

1. Verificar que PostgreSQL está agregado
2. Esperar 30 segundos a que Railway cree la BD
3. Revisar logs: `railway logs`
4. Verificar que `DATABASE_URL` está en variables

### Error: "CORS blocked"

Actualizar `CORS_ORIGINS` en variables de entorno con la URL correcta:
```bash
railway variables set CORS_ORIGINS=https://tu-app.railway.app
```

---

## 📊 MONITOREO

### Ver uso de recursos
```bash
railway status
```

### Ver variables de entorno
```bash
railway variables
```

### Actualizar variable
```bash
railway variables set NOMBRE=valor
```

### Ver historial de deploys
```bash
railway deployments
```

---

## 🔄 ACTUALIZAR LA APP

Después de hacer cambios locales:

```bash
# Commit y push a GitHub
git add .
git commit -m "Descripción del cambio"
git push

# Railway redeploya automáticamente
# Ver logs:
railway logs
```

---

## 🎯 CHECKLIST RÁPIDO

```bash
# 1. Preparar
cd backend
copy ..\\.env.example .env
# Editar .env

# 2. Probar localmente (opcional)
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py

# 3. Subir a GitHub
cd ..
git init
git add .
git commit -m "Ready for Railway"
git remote add origin https://github.com/TU_USUARIO/get-fit.git
git push -u origin main

# 4. En Railway web UI:
# - Conectar GitHub repo
# - Agregar PostgreSQL
# - Configurar variables de entorno
# - Configurar Build & Deploy

# 5. Verificar
railway logs
railway open
```

---

## 💡 TIPS ÚTILES

### Generar claves seguras
```bash
# PowerShell
[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString() + (New-Guid).ToString())) | Select-Object -First 32
```

O simplemente usar:
```
SECRET_KEY=my-super-secret-key-change-this-in-production-12345
JWT_SECRET_KEY=my-jwt-secret-key-change-this-in-production-12345
```

### Ver archivos en Railway
```bash
railway shell
ls -la
```

### Ejecutar comando en Railway
```bash
railway run python -c "from app import create_app; app = create_app(); print('OK')"
```

---

## 🚀 RESUMEN FINAL

1. ✅ Crear `.env`
2. ✅ Push a GitHub
3. ✅ Conectar Railway
4. ✅ Agregar PostgreSQL
5. ✅ Configurar variables
6. ✅ ¡Listo!

**Tiempo total: 15-20 minutos**

¿Necesitas ayuda? Revisa los logs con `railway logs`
