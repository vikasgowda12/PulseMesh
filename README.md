# PulseMesh

PulseMesh is an incident management MVP with a FastAPI REST and GraphQL API, a React dashboard, PostgreSQL storage, and optional Kafka event publishing. The gRPC server and Kafka consumer are separate processes and are not started by the web service.

## Local development

Start the local PostgreSQL and Kafka services from the repository root:

```sh
docker compose up -d
```

Copy `backend/.env.example` to `backend/.env` and install the backend requirements. Then run the API from `backend`:

```sh
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend loads `backend/.env`. The example config uses PostgreSQL on port 5433, matching `compose.yaml`, and Kafka on `localhost:9092`. Run the frontend from `frontend` after copying `frontend/.env.example` to `frontend/.env`:

```sh
npm ci
npm run dev
```

The API initializes missing tables once when the web application starts. It uses SQLAlchemy `create_all`; it does not alter existing tables or replace data.

## Render deployment

Deploy the existing `pulsemesh-db` PostgreSQL database and both application services in the Ohio region. Do not paste database URLs or credentials into source control or chat.

### PostgreSQL

Use the existing `pulsemesh-db` database. In its Render dashboard, copy the **Internal Database URL** using Render's copy control. In the backend service's environment settings, create `DATABASE_URL` and paste the copied value directly into that field. The backend converts Render's `postgres://` or `postgresql://` scheme to the installed `psycopg` driver format. Keep the database and backend in the same Render account/workspace and Ohio region so the backend can use the internal address.

### Backend web service

- **Root directory:** `backend`
- **Runtime:** Python
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health`

Set these environment variables in the Render service:

- `DATABASE_URL`: Internal Database URL copied from `pulsemesh-db`.
- `FRONTEND_URLS`: Comma-separated allowed browser origins. After the frontend is deployed, set this to its Render URL (for example, `https://your-site.onrender.com`). Include additional origins separated by commas only when needed. Local origins are used by default when this setting is absent.
- `KAFKA_BOOTSTRAP_SERVERS`: Leave unset or empty to disable Kafka publishing in this deployment. Set to a reachable broker address only if you separately provision Kafka.
- `KAFKA_TOPIC`: Optional; defaults to `incident-events`.

No production database password or frontend address belongs in the repository. GraphQL is available on the same backend at `/graphql`. The `/health` endpoint reports web process health; database connectivity is checked during startup while tables initialize.

### Frontend static site

- **Root directory:** `frontend`
- **Build command:** `npm ci && npm run build`
- **Publish directory:** `dist`
- **Environment variable:** `VITE_API_URL` set to the deployed backend base URL, with no trailing slash (for example, `https://your-api.onrender.com`).

Add a Render rewrite rule for client-side routing: source `/*`, destination `/index.html`, action `Rewrite`. The current dashboard uses the API base URL for listing, creating, and resolving incidents. The backend also supports retrieving an individual incident over REST.

## Optional services and schema changes

The deployed demo includes the React dashboard, FastAPI REST/GraphQL endpoints, and PostgreSQL. Kafka publishing is disabled unless a broker is configured; when enabled, broker failures are logged and do not fail incident creation. Events are not queued for later delivery. Kafka streaming requires a separately hosted, reachable broker and a separately run consumer. No Kafka service is created by these instructions.

The gRPC server is also not part of the Render web process. It would need a separately deployed service and an appropriate network configuration to be reachable externally.

There are no Alembic migrations in this repository. Startup uses `Base.metadata.create_all()` to create missing tables. This is adequate for the current MVP schema, but it will not apply schema changes to existing tables; add and run migrations before evolving a production schema.
