# 🚀 Content Hub · Dashboard Multi-Canal

Aplicación web unificada para gestionar, auditar y generar contenido diario optimizado para:
1. **Marca Personal:** `@s_thiago7` (Instagram) & `@santiagoquevedo71` (TikTok).
2. **Empresa B2B:** `@nodo_tg` (Instagram) & `@nodotechgrowth` (TikTok) alineada a [conectanodo.com](https://www.conectanodo.com).
3. **Analíticas de TikTok Studio:** Radiografía de rendimiento basada en datos de `Overview.csv`.

---

## 📁 Estructura del Proyecto

```text
content_hub/
├── app.py                  # Servidor Starlette / Uvicorn con endpoints REST
├── requirements.txt        # Dependencias (starlette, uvicorn, requests)
├── Procfile                # Configuración de despliegue en la nube (Render / Railway)
├── run.bat                 # Lanzador de 1 clic para Windows
├── .gitignore              # Archivos ignorados por Git
├── data/
│   ├── config.json         # Tokens oficiales de Meta Graph API y TikTok Sandbox
│   └── tiktok_studio.json  # Métricas parseadas de TikTok Studio (Overview.csv)
├── services/
│   ├── meta_service.py     # Lógica de conexión a Instagram API y generador de guiones
│   └── tiktok_service.py   # Scraper en vivo y matriz de ganchos virales
└── templates/
    └── index.html          # Interfaz web interactiva en modo oscuro (Tailwind CSS)
```

---

## ⚡ Inicio Rápido Local (Windows)

### Opción 1: Lanzador de 1 Clic
Simplemente haz doble clic sobre el archivo **`run.bat`**.  
Abrirá automáticamente tu navegador en **`http://localhost:8000`** e iniciará el servidor.

### Opción 2: Desde Terminal
```powershell
pip install -r requirements.txt
python app.py
```
Abre en tu navegador: `http://localhost:8000`

---

## 🌐 Despliegue Gratuito en la Nube (Acceso desde el móvil / sin localhost)

Si no quieres depender de tener tu computadora prendida o de `localhost`, puedes subir este proyecto a GitHub y desplegarlo gratis en **Render** o **Railway**:

### 1. Subir a GitHub
```bash
git init
git add .
git commit -m "feat: Content Hub v2.0 multi-channel app"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

### 2. Desplegar en Render (1 Clic)
1. Entra a [render.com](https://render.com) y conecta tu repositorio de GitHub.
2. Selecciona **New Web Service**.
3. Configuración:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
4. Haz clic en **Deploy**.  
   *¡Te dará una URL pública tipo `https://tu-content-hub.onrender.com` con HTTPS lista para abrir desde cualquier dispositivo!*

---

## 🎯 Canales y Módulos

### 1. Marca Personal (`@s_thiago7`)
- Métricas en vivo (Seguidores, publicaciones, crecimiento 24h).
- Generador de 8 Reels diarios con horarios sugeridos espaciados (evita canibalización algorítmica).
- Botones de 1 clic para copiar texto en pantalla y copy al portapapeles.

### 2. Empresa B2B (`@nodo_tg` / conectanodo.com)
- Métricas en vivo del perfil empresarial.
- 2 Reels diarios de dolores de negocios (WhatsApp desordenado, cotizaciones en PDF olvidadas, Método NODO RUTA).
- Enlace directo a conectanodo.com y WhatsApp oficial.

### 3. TikTok Strategy & Analíticas de TikTok Studio
- Comparativa real de los últimos 7 días basada en datos crudos de `Overview.csv`.
- Diagnóstico del pico de 690 vistas (storytelling) vs la caída a 17 vistas en Nodo.
- Matriz de ganchos virales para el 90% de audiencia femenina en la cuenta personal.
- Estrategia de SEO por intención de búsqueda (Search-Intent).
