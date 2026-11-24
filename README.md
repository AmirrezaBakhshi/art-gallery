# ArtGallery

ArtGallery is a React + Django REST Framework application for galleries and museums to publish artwork collections with images, descriptions, audio, and video. Visitors can browse public collections; gallery operators can manage their own collection after signing in.

## Architecture

- `frontend/`: React 18 application built with Vite.
- `backend/`: Django 5.2 LTS and Django REST Framework API.
- SQLite is used by default only for local development. Production requires PostgreSQL via `DATABASE_URL`; startup fails if it is missing or uses another database engine.

## Requirements

- Python 3.10+
- Node.js 22+
- npm

## Local development

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

The API is available at `http://localhost:8000`. For local development, the default settings use SQLite and allow the Vite origin at `http://localhost:5173`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `frontend/.env` if the API is not running at `http://localhost:8000`. Set `VITE_SCANNER_URL` only if you have deployed the optional scanner application.

## API overview

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/gallaries/` | Public registration |
| GET | `/api/auth/csrf/` | Public CSRF bootstrap; returns a masked token for the `X-CSRFToken` header |
| POST | `/api/auth/login/` | Public login; establishes HttpOnly session cookie |
| POST | `/api/auth/logout/` | Authenticated gallery; revokes current session |
| GET | `/api/gallaries/` | Public gallery directory |
| GET | `/api/gallaries/{id}/` | Public gallery profile |
| PATCH / PUT | `/api/gallaries/{id}/` | Owning gallery |
| GET | `/api/items/` | Public artwork collection |
| POST | `/api/items/` | Authenticated gallery |
| GET | `/api/items/{id}/` | Public artwork |
| GET | `/api/targetfiles/` | Authenticated owning gallery only |
| POST | `/api/targetfiles/` | Authenticated gallery |
| GET | `/api/targetfiles/{id}/` | Authenticated owning gallery only |
| PUT / PATCH / DELETE | `/api/targetfiles/{id}/` | Owning gallery |
| PATCH / PUT / DELETE | `/api/items/{id}/` | Owning gallery |

Gallery sessions use an expiring, HttpOnly, Secure (in production), SameSite cookie. Unsafe cookie-authenticated requests require a CSRF token. Raw session tokens are never returned in JSON or stored in browser localStorage; only SHA-256 token digests are stored in the database. Existing plaintext passwords and bearer tokens are converted by the `0005_hash_legacy_credentials` migration. The `0006_gallery_token_expiry` migration assigns a 14-day expiry to existing sessions. Users with invalid or expired sessions must sign in again.

## Configuration

See `backend/.env.example`. In production, set a unique `DJANGO_SECRET_KEY` (at least 50 characters), disable debug mode, configure `DJANGO_ALLOWED_HOSTS`, configure trusted CORS/CSRF origins, and use HTTPS. If TLS terminates at a trusted reverse proxy, set `DJANGO_TRUST_PROXY_SSL_HEADER=true` only when that proxy overwrites the `X-Forwarded-Proto` header. HSTS does not include subdomains by default; enable that only after confirming every subdomain supports HTTPS. Set `DJANGO_COOKIE_SAMESITE=None` only when the frontend and API are on different sites; HTTPS is mandatory in that case. The frontend receives a masked CSRF token from the API's CSRF bootstrap endpoint; keep the CSRF cookie host-only unless your deployment has a specific reason to widen its domain. Use a shared cache for rate limiting across multiple application workers. Do not use the example values in a public deployment.

## Tests and quality checks

```bash
cd backend
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

```bash
cd frontend
npm ci
npm run lint
npm run build
```

## Security notes

- Gallery passwords are write-only at the API boundary and stored as Django password hashes.
- Gallery write operations and artwork mutations require an authenticated session. Browser sessions use HttpOnly cookies and CSRF validation.
- Artwork ownership is checked on update and delete.
- Gallery directory/profile responses omit email, address, and contact details. Those fields remain available to the authenticated gallery owner. Artwork reads remain public. Target-file list/detail endpoints are restricted to the owning authenticated gallery. **Production media hosting must additionally deny public HTTP access to the `target_file/` storage directory**; protecting an API endpoint does not secure a separately exposed static media URL.
- Media uploads should be served from a dedicated media service in production; Django's development media serving is enabled only when `DEBUG` is true. API upload validation caps target images at 10 MB, audio at 25 MB, videos at 100 MB, and target files at 50 MB. The reverse proxy or ingress must also enforce an appropriate request-body limit. Extension checks are defense-in-depth, not malware scanning or proof of file contents.
