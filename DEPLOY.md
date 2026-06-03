# Despliegue en Supabase + Render

La app corre en **Render** y los datos se guardan en **Supabase** (PostgreSQL).

---

## Paso 1 — Subir el código a GitHub

1. Cree una cuenta en [github.com](https://github.com) si no tiene.
2. Cree un repositorio nuevo (por ejemplo: `servicios-gps-llaves`).
3. En PowerShell, dentro de la carpeta del proyecto:

```powershell
cd "c:\Users\crist\OneDrive\Documentos\software llaves y gps"
git init
git add .
git commit -m "App gestión servicios GPS y llaves"
git branch -M main
git remote add origin https://github.com/SU_USUARIO/servicios-gps-llaves.git
git push -u origin main
```

(Sustituya `SU_USUARIO` y el nombre del repo por los suyos.)

---

## Paso 2 — Crear base de datos en Supabase

1. Entre a [supabase.com](https://supabase.com) y cree un proyecto.
2. Vaya a **Project Settings → Database**.
3. En **Connection string**, elija **URI** y copie la URL.
   - Debe verse así:
     `postgresql://postgres.[ref]:[PASSWORD]@aws-0-xxx.pooler.supabase.com:6543/postgres`
   - O la directa en el puerto `5432`.
4. (Opcional) En **SQL Editor**, puede ejecutar el archivo `supabase_schema.sql`.
   - Si no lo hace, la app crea las tablas al arrancar.

Guarde la **contraseña** de la base de datos; la necesitará en Render.

---

## Paso 3 — Desplegar en Render

1. Entre a [render.com](https://render.com) y conecte su cuenta de GitHub.
2. **New → Web Service**.
3. Seleccione el repositorio del proyecto.
4. Configuración recomendada:

| Campo | Valor |
|-------|--------|
| **Name** | servicios-gps-llaves |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Plan** | Free |

5. En **Environment Variables**, agregue:

| Key | Value |
|-----|--------|
| `DATABASE_URL` | La URL de Supabase (connection string completa) |
| `PYTHON_VERSION` | `3.12.0` |

6. Pulse **Create Web Service** y espere el deploy (2–5 minutos).

7. Cuando termine, Render le dará una URL como:
   `https://servicios-gps-llaves.onrender.com`

Abra esa URL en el navegador: la app ya está en línea.

---

## Uso local con Supabase (opcional)

Si quiere probar en su PC usando la misma base de datos en la nube:

1. Copie `.env.example` a `.env`.
2. Pegue su `DATABASE_URL` de Supabase.
3. Instale dependencias e inicie:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Sin `DATABASE_URL`, la app sigue usando SQLite local (`servicios.db`).

---

## Notas importantes

- **Plan free de Render**: la app se “duerme” tras ~15 min sin uso; el primer acceso puede tardar ~30 s en despertar.
- **Supabase free**: incluye 500 MB de base de datos, suficiente para este uso.
- **Backups**: en Supabase puede exportar datos desde el panel o SQL Editor.
- **Seguridad**: no suba `.env` ni contraseñas a GitHub (ya están en `.gitignore`).

---

## Resumen de archivos de despliegue

| Archivo | Función |
|---------|---------|
| `render.yaml` | Configuración automática para Render |
| `Procfile` | Comando de inicio en producción |
| `runtime.txt` | Versión de Python |
| `supabase_schema.sql` | Tablas en Supabase (opcional) |
| `.env.example` | Ejemplo de variable de entorno |
