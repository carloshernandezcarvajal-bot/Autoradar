# Autoradar — Información de la Conversación

## Visión General

**Autoradar** es un buscador inteligente de vehículos en Colombia. Su objetivo principal es ser el mejor buscador de carros del país, permitiendo a los usuarios encontrar, comparar y recibir alertas sobre publicaciones de vehículos en múltiples plataformas.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | FastAPI (Python 3.12+) |
| **Frontend** | Next.js 15 (React 19, TypeScript) |
| **Base de datos** | PostgreSQL 16 (via SQLAlchemy asyncio) |
| **Autenticación** | JWT (python-jose) + bcrypt |
| **Scraping** | Playwright + httpx |
| **Estilos** | Tailwind CSS 4 |
| **Íconos** | Lucide React |
| **Infraestructura** | Railway (backend + db) |

---

## Estado Actual del Proyecto

- **MVP v1 completado** y comiteado (`cf168cd v1: MVP inicial - Autoradar`)
- Repositorio: `https://github.com/carloshernandezcarvajal-bot/Autoradar`
- Railway configurado con `railway.json` (build via Dockerfile)
- El frontend tiene páginas: inicio (`/`), favoritos (`/favoritos`), alertas (`/alertas`)
- Último commit (`e0f30c0`): `fix: switch to python 3.12-slim, add system deps for playwright, add aiosqlite`

---

## Lo Implementado en Esta Sesión

### 1. Puerto Dinámico para Railway
- **Archivo:** `backend/Dockerfile`
- Cambio: `CMD` ahora usa `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`
- Railway inyecta `PORT`, con fallback a `8000`

### 2. Endpoint de Scraping + Scheduler
- **Archivos creados:**
  - `backend/app/routers/scraper.py` — `POST /api/scrape` (autenticado) + `GET /api/scrape/status`
  - `backend/app/services/scraper_service.py` — Orquesta scraping y persistencia en DB
- **Archivo modificado:** `backend/app/main.py`
  - Se registró el router `scraper`
  - Se agregó scheduler automático cada 1 hora (background task asyncio)
- Los scrapers existentes (`TuCarroScraper`, `CarroYaScraper`) persisten en DB:
  - Busca o crea `Vehicle` (por brand + model + year)
  - Crea o actualiza `Listing`
  - Registra `PriceHistory` si el precio cambió

### 3. Persistencia de Auth en Frontend
- **Archivo:** `frontend/src/components/Navbar.tsx`
- Se agregó `useEffect` que al montar el componente:
  1. Busca token en `localStorage`
  2. Si existe, llama a `GET /api/auth/me` para obtener el usuario
  3. Si el token es inválido, lo limpia
- Ahora al refrescar la página la sesión persiste

### 4. Configuración para Producción (Railway)
- **Archivo:** `backend/app/config.py`
  - Se agregó auto-conversión de `DATABASE_URL`: si Railway pasa `postgresql://...`, automáticamente se convierte a `postgresql+asyncpg://...`
- **Archivo:** `.env.example`
  - Se actualizó con claves de ejemplo generadas
  - Documentación de variables de entorno

### 5. Fix Build de Railway
- **Archivo:** `backend/Dockerfile`
  - Cambio de `python:3.14-slim` a `python:3.12-slim` (compatibilidad)
  - Se agregaron dependencias del sistema para Playwright
  - Separación de `pip install` y `playwright install` para mejor cacheo
- **Archivo:** `backend/requirements.txt`
  - Se agregó `aiosqlite==0.20.0` (necesario para SQLite local)

### 6. Fix de Endpoint de Favoritos (Pydantic Schema)
- **Archivos:** `backend/app/schemas/schemas.py`, `backend/app/routers/favorites.py`
  - Se creó el esquema `FavoriteCreate` para recibir el `listing_id` en el cuerpo del JSON (POST `/api/favorites`).
  - Se actualizó el endpoint en `favorites.py` para usar este esquema, resolviendo el error 422 de FastAPI (Unprocessable Entity) al agregar favoritos desde el cliente.

---

## Estado del Deploy (Railway)

**Pendiente:** El backend está en `Build Failed`. Se hizo un commit de fix (`e0f30c0`) que debe pushearse para que Railway lo reconstruya.

**Dockerfile actual (`backend/Dockerfile`):**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libxshmfence1 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install chromium

COPY . .

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Variables de entorno configuradas en Railway (backend):**
| Variable | Valor |
|----------|-------|
| `SECRET_KEY` | `38360764c022310fa991220eea4cdc9094c12cb1972f6005232d5168ebbd8309` |
| `ENCRYPTION_KEY` | `c4d1d7c02b868d3e6266cbe6637de7f14b95c55e95240b78169265bf2160de70` |
| `CORS_ORIGINS` | `https://autoradar-five.vercel.app` |
| `ENVIRONMENT` | `production` |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:****@postgres.railway.internal:5432/railway` |

**Pasos que faltan para completar el deploy:**
1. `git push origin main` desde la terminal del usuario
2. Esperar que Railway reconstruya el backend automáticamente
3. Generar dominio público en el servicio backend (Settings → Networking → Generate Domain)
4. Crear servicio frontend en Railway (o dejarlo en Vercel como está)
5. Configurar `NEXT_PUBLIC_API_URL` en el frontend con la URL del backend

---

## Requisitos del Proyecto (de `informacion.txt`)

- **Mercado objetivo:** Colombia
- **Presupuesto:** $50.000 - $150.000 COP/mes en infraestructura
- **Dedicación:** 5-10 horas/semana
- **Usuarios:** Sistema con registro desde el MVP (guardar búsquedas, alertas, favoritos)
- **Fotos:** No almacenar, solo enlaces
- **Marketplace Facebook:** Postergado a fase futura
- **IA:** Primero construir buscador, luego IA
- **Precios:** Gratis al principio; monetizar con historial de precios, reporte de fraudes y recomendador inteligente
- **Demo:** `demo@autoradar.co / demo123`

## Funcionalidades Deseadas por el Usuario

- Detectar oportunidades de vehículos según parámetros (modelo, precio, ubicación, kilometraje)
- Notificaciones automáticas
- Comparación visual de vehículos de diferentes páginas
- Detección de publicaciones duplicadas
- Detección de posibles fraudes
- Comparación con modelos de concesionario
- Buscador inteligente por necesidades (familia, deportivo, pet friendly, etc.)

---

## Próximos Pasos (Priorizados)

| Prioridad | Paso | Archivos involucrados |
|-----------|------|----------------------|
| 🔴 1 | **Pushear fix del build** | `git push origin main` |
| 🔴 2 | **Deploy backend en Railway** | Dashboard Railway |
| 🟡 3 | **Deploy frontend en Railway (o Vercel)** | Dashboard Railway |
| 🟡 4 | **Página de detalle de vehículo** | `frontend/src/app/vehiculo/[id]/page.tsx` |
| 🟢 5 | **Visualización de historial de precios** | Componente gráfico en frontend |
| 🟢 6 | **Notificaciones de alertas** | Email/push notifications |
| 🟢 7 | **Registro de usuarios con confirmación** | Email verification |

---

## Estructura del Proyecto

```
Autoradar/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py           # Config (auto-convierte DATABASE_URL)
│   │   ├── database.py         # SQLAlchemy async engine
│   │   ├── main.py             # FastAPI app + scheduler scraping
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── vehicle.py
│   │   │   ├── listing.py
│   │   │   ├── alert.py
│   │   │   ├── favorite.py
│   │   │   └── price_history.py
│   │   ├── routers/
│   │   │   ├── auth.py         # POST /register, /login, GET /me
│   │   │   ├── vehicles.py     # CRUD vehículos, price-history
│   │   │   ├── search.py       # POST /api/search
│   │   │   ├── alerts.py       # CRUD alertas
│   │   │   ├── favorites.py    # CRUD favoritos
│   │   │   └── scraper.py      # POST /api/scrape, GET /status
│   │   ├── schemas/
│   │   │   └── schemas.py      # Pydantic modelos
│   │   └── services/
│   │       ├── scraper.py          # TuCarroScraper, CarroYaScraper
│   │       ├── scraper_service.py  # Orquestación + persistencia
│   │       ├── normalization.py    # Normalización de marcas/modelos
│   │       ├── opportunity_score.py # Score 0-100
│   │       ├── analytics.py        # Price history
│   │       └── encryption.py       # Encriptación
│   ├── Dockerfile
│   ├── railway.json
│   ├── requirements.txt
│   ├── seed.py                # 30 vehículos de muestra
│   └── test_*.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx           # Home con buscador
│   │   │   ├── layout.tsx
│   │   │   ├── globals.css
│   │   │   ├── favoritos/page.tsx
│   │   │   └── alertas/page.tsx
│   │   ├── components/
│   │   │   ├── Navbar.tsx         # Auth modal + persistencia
│   │   │   ├── SearchBar.tsx      # Filtros (marca, modelo, año, precio, km)
│   │   │   ├── ResultsGrid.tsx    # Resultados + market stats
│   │   │   ├── VehicleCard.tsx    # Card individual
│   │   │   └── ComparisonModal.tsx # Comparación hasta 4 vehículos
│   │   ├── lib/
│   │   │   └── api.ts             # Cliente API (fetch + auth)
│   │   └── types/
│   │       └── index.ts           # TypeScript interfaces
│   ├── Dockerfile
│   ├── next.config.ts
│   ├── package.json
│   └── vercel.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── informacion.txt
```

---

## Endpoints de la API

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/api/health` | No | Health check |
| `POST` | `/api/auth/register` | No | Registrar usuario |
| `POST` | `/api/auth/login` | No | Iniciar sesión (devuelve JWT) |
| `GET` | `/api/auth/me` | Sí | Obtener usuario actual |
| `POST` | `/api/search` | No | Buscar vehículos (filtros + paginación) |
| `GET` | `/api/vehicles` | No | Listar vehículos |
| `GET` | `/api/vehicles/{id}` | No | Detalle listing + opportunity score |
| `GET` | `/api/vehicles/{id}/price-history` | No | Historial de precios |
| `GET` | `/api/vehicles/brands/list` | No | Lista de marcas |
| `GET` | `/api/vehicles/models/list` | No | Lista de modelos (filtrable por marca) |
| `GET` | `/api/alerts` | Sí | Listar alertas del usuario |
| `POST` | `/api/alerts` | Sí | Crear alerta |
| `DELETE` | `/api/alerts/{id}` | Sí | Eliminar alerta |
| `GET` | `/api/favorites` | Sí | Listar favoritos |
| `POST` | `/api/favorites` | Sí | Agregar favorito |
| `DELETE` | `/api/favorites/{id}` | Sí | Quitar favorito |
| `POST` | `/api/scrape` | Sí | Ejecutar scraping manual |
| `GET` | `/api/scrape/status` | No | Estado del scraping |

---

## Comandos Útiles

```bash
# Desarrollo local (todo junto)
docker-compose up --build

# Backend standalone
cd backend && uvicorn app.main:app --reload

# Frontend standalone
cd frontend && npm run dev

# Seed de datos de prueba
cd backend && python seed.py

# Ejecutar scraping manual (requiere token)
curl -X POST http://localhost:8000/api/scrape \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"sources": ["tucarro"]}'

# Ver estado del scraper
curl http://localhost:8000/api/scrape/status
```
