# 🚀 DESPLIEGUE EN RAILWAY - GUÍA RÁPIDA

## ✅ ESTADO DEL PROYECTO

Tu proyecto **ESTÁ CASI LISTO** para desplegar. He corregido los problemas principales:

✅ Base de datos: Ahora usa variables de entorno  
✅ Rutas de archivos: Corregidas para Railway  
✅ Procfile: Creado  
✅ Variables de entorno: Archivo .env.example creado  

---

## 🎯 PASOS PARA DESPLEGAR (5 MINUTOS)

### 1️⃣ PREPARAR LOCALMENTE

```bash
# Ir a la carpeta del proyecto
cd c:\Users\ElixirStudio\Desktop\get-fit-main\get-fit-main\gym-system

# Crear archivo .env en backend/
cd backend
copy ..\\.env.example .env

# Editar .env y cambiar:
# - SECRET_KEY=algo-aleatorio-aqui
# - JWT_SECRET_KEY=algo-aleatorio-aqui
```

### 2️⃣ SUBIR A GITHUB

```bash
# Volver a la raíz
cd ..

# Inicializar git
git init
git add .
git commit -m "Gym system ready for Railway deployment"

# Crear repo en GitHub (web)
# Luego:
git remote add origin https://github.com/TU_USUARIO/get-fit.git
git branch -M main
git push -u origin main
```

### 3️⃣ DESPLEGAR EN RAILWAY

1. Ir a https://railway.app
2. Hacer clic en **"Start a New Project"**
3. Seleccionar **"Deploy from GitHub"**
4. Autorizar GitHub y seleccionar el repo `get-fit`
5. Railway detectará automáticamente que es Python/Flask

### 4️⃣ CONFIGURAR EN RAILWAY

**Agregar Base de Datos:**
- Click en **"+ Add Service"**
- Seleccionar **"Database"** → **"PostgreSQL"**
- Railway crea automáticamente `DATABASE_URL`

**Agregar Variables de Entorno:**
- En el servicio web, ir a **"Variables"**
- Agregar:
  ```
  FLASK_ENV=production
  SECRET_KEY=generar-algo-aleatorio-aqui
  JWT_SECRET_KEY=generar-algo-aleatorio-aqui
  CORS_ORIGINS=https://tu-app.railway.app
  ```

**Configurar Build & Deploy:**
- Build Command: `pip install -r backend/requirements.txt`
- Start Command: `cd backend && python app.py`
- Port: `5000`

### 5️⃣ ¡LISTO!

Tu app estará en: `https://tu-app.railway.app`

---

## 🐛 SI ALGO FALLA

### Error: "ModuleNotFoundError: No module named 'gym'"
**Solución**: Cambiar Start Command a:
```
cd backend && PYTHONPATH=/app/backend python app.py
```

### Error: "No such file or directory: 'frontend'"
**Solución**: Verificar que la estructura en GitHub es:
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

### Error: "Database connection failed"
**Solución**: 
1. Verificar que PostgreSQL está agregado como servicio
2. Esperar 30 segundos a que Railway cree la BD
3. Revisar los logs en Railway

---

## 💡 TIPS

- **Gratis**: Railway da 5 USD/mes de crédito (suficiente para una app pequeña)
- **Actualizaciones**: Cada push a GitHub redeploya automáticamente
- **Logs**: En Railway → "Logs" para ver errores
- **Dominio**: Railway te da uno, o conecta el tuyo

---

## 📝 CHECKLIST FINAL

- [ ] Archivo `.env` creado en `backend/`
- [ ] Proyecto subido a GitHub
- [ ] Cuenta en Railway creada
- [ ] PostgreSQL agregado como servicio
- [ ] Variables de entorno configuradas
- [ ] Build & Deploy configurado
- [ ] App desplegada y funcionando

¡Listo! 🎉
