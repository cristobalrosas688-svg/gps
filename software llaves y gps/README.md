# Gestión de Servicios — GPS y Llaves

Aplicación local para organizar servicios de **Mavi GPS**, **Tei GPS** y **Egaña Automotriz** (llaves), con exportación a PDF por empresa.

## Requisitos

- Windows con **Python 3.10+** instalado ([python.org](https://www.python.org/downloads/))
- Al instalar Python, marque **"Add Python to PATH"**

## Cómo iniciar

1. Haga doble clic en **`iniciar.bat`**
2. Se abrirá el servidor; en el navegador vaya a: **http://127.0.0.1:5000**

O manualmente en una terminal:

```bash
cd "c:\Users\crist\OneDrive\Documentos\software llaves y gps"
pip install -r requirements.txt
python app.py
```

## Funciones

### Mavi GPS y Tei GPS

- Código de identificación
- Ubicación del servicio
- Distancia recorrida (km)
- Vehículo: marca, modelo, patente
- Fecha y notas opcionales
- **Descargar PDF mensual**: elija el mes y descargue solo los servicios de ese período

### Egaña Automotriz (llaves)

- Vehículo: marca, modelo, patente
- Valor de insumos y cobro del servicio
- **Ganancia** calculada automáticamente (cobro − insumos)
- Resumen de totales en pantalla
- **Descargar PDF mensual** con reporte y totales del mes seleccionado

## Datos

- **Local**: los registros se guardan en `servicios.db` (SQLite).
- **En la nube**: use Supabase (PostgreSQL). Ver guía completa en **[DEPLOY.md](DEPLOY.md)**.

## Despliegue (Supabase + Render)

Instrucciones paso a paso en **[DEPLOY.md](DEPLOY.md)**:
1. Subir código a GitHub
2. Crear proyecto y base de datos en Supabase
3. Desplegar en Render con la variable `DATABASE_URL`

## Estructura

```
app.py           — Servidor web
database.py      — Base de datos SQLite
pdf_export.py    — Generación de PDF
templates/       — Interfaz web
static/          — Estilos y JavaScript
servicios.db     — Datos (se crea al usar la app)
```
