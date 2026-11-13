# Storytelling Bibivaiafeira

A simple web application that displays an image based on a status stored on the server.

## Technology stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL (Neon in production)
- Server-Sent Events (SSE) for real-time screen updates
- Render for hosting

## How it works

The `GET /bibivaiafeira` page displays the image associated with the current status. The browser keeps an SSE connection open at `/api/events`. When the status changes, the server sends an event and the page switches images **without reloading**.

Supported statuses:

- `start`
- `products`
- `purchase`

The sample images are in `app/static/images/`. Replace the SVGs with your own images, keeping the filenames `start.svg`, `products.svg`, and `purchase.svg` (or update the mapping in `app/main.py`).

## Run locally

Requires Python 3.11 or later.

```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Page: http://localhost:8000/bibivaiafeira
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

The application loads `.env.local` and then `.env` from the project root. Variables already set in the environment take precedence. Without `DATABASE_URL`, it uses a local SQLite database (`storytelling.db`).

The project is linked to Neon through `.neon` (ignored by Git). To refresh local credentials, run `neon deploy`; it applies `neon.ts` and writes the variables to `.env.local`. Never commit this file to Git.

Queries use `DATABASE_URL` (a pooled connection). When available, `DATABASE_URL_UNPOOLED` is used to create tables at startup. On Render, configure both variables with the Neon values; `.env.local` is not included in the deployment.

## API

### Get the current status

```http
GET /api/status
```

Example response:

```json
{
  "status": "start",
  "image": "/static/images/start.svg"
}
```

### Update the status

The `POST /bibivaiafeira` endpoint accepts the status as a query parameter:

```bash
curl -X POST "http://localhost:8000/bibivaiafeira?status=products"
```

Example response fields (the response also includes a `message` field containing a success message in Portuguese):

```json
{
  "status": "products",
  "image": "/static/images/products.svg"
}
```

Allowed values: `start`, `products`, `purchase`. An invalid value returns HTTP 422 through FastAPI's automatic validation.

### Real-time updates

The browser connects to:

```http
GET /api/events
```

This route uses Server-Sent Events. The server checks the stored status every second and sends an event when it detects a change. The page does not need to refresh. The browser's EventSource automatically attempts to reconnect if the connection drops.

## Deploy on Render + Neon

### 1. Create the database on Neon

1. Create an account at https://neon.com/.
2. Create a PostgreSQL project.
3. Copy the connection strings in PostgreSQL format.
4. Save them to configure `DATABASE_URL` and `DATABASE_URL_UNPOOLED` on Render.

### 2. Publish the code on GitHub

Create a GitHub repository and push the project files to its root, excluding credentials and other files ignored by Git.

### 3. Create the service on Render

1. Go to https://render.com/ and connect your GitHub account.
2. Choose **New > Blueprint** (or create a **Web Service** pointing to the repository).
3. The `render.yaml` file configures the build, startup command, and health check.
4. Set `DATABASE_URL` to the pooled Neon connection string and `DATABASE_URL_UNPOOLED` to the direct connection string.
   - If Neon provides a `postgresql://...` URL, the application automatically converts it to use the `psycopg` driver.
5. Deploy the service.

After deployment, the page will be available at:

```text
https://YOUR-SERVICE.onrender.com/bibivaiafeira
```

The service name and subdomain depend on availability on Render. To include `storytelling` in the domain, choose a service name such as `storytelling-bibivaiafeira`, if available. A custom `.com.br` domain must be registered separately.

## Free plan notes

- Render's free web service may spin down after a period without traffic; the first visit afterward may take longer to respond.
- Neon's database has its own free plan limits. Check the provider's website for current limits.
- An external PostgreSQL database is important because a free service's local disk may be ephemeral. Do not use local SQLite for production persistence.
- This MVP does not implement authentication, as requested. Anyone who knows the POST URL can change the status. Do not publish sensitive data through this service.
- To keep SSE simple, the service queries the database every second for each open connection. This is a straightforward approach for this MVP and a small instance; if the audience grows significantly, consider switching to notifications or pub/sub.

## Project structure

```text
.
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/styles.css
│       ├── js/app.js
│       └── images/
│           ├── start.svg
│           ├── products.svg
│           └── purchase.svg
├── requirements.txt
├── Procfile
├── render.yaml
└── README.md
```
