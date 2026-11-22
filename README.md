# ArtGallery

ArtGallery is a React + Django REST Framework application for galleries and museums to publish artwork collections with images, descriptions, audio, and video. Visitors can browse public collections; gallery operators can manage their own collection after signing in.

## Architecture

- `frontend/`: React 18 application built with Vite.
- `backend/`: Django 5.1 and Django REST Framework API.
- SQLite is used by default for local development. PostgreSQL can be configured with `DATABASE_URL`.

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
| POST | `/api/auth/login/` | Public login |
| POST | `/api/auth/logout/` | Authenticated gallery; revokes current token |
| GET | `/api/gallaries/` | Public gallery directory |
| GET | `/api/gallaries/{id}/` | Public gallery profile |
| PATCH / PUT | `/api/gallaries/{id}/` | Owning gallery |
| GET | `/api/items/` | Public artwork collection |
| POST | `/api/items/` | Authenticated gallery |
| GET | `/api/items/{id}/` | Public artwork |
| PATCH / PUT / DELETE | `/api/items/{id}/` | Owning gallery |

Authenticated requests use `Authorization: Bearer <token>`. Passwords are hashed server-side and are never returned by the API. Existing plaintext passwords are upgraded to Django password hashes after a successful legacy login.

## Configuration

See `backend/.env.example`. In production, set a unique `DJANGO_SECRET_KEY`, disable debug mode, configure `DJANGO_ALLOWED_HOSTS`, configure trusted CORS/CSRF origins, and use HTTPS. Do not use the development defaults in a public deployment.

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
- Gallery write operations and artwork mutations require a bearer token.
- Artwork ownership is checked on update and delete.
- Public read endpoints intentionally expose public gallery and artwork information only.
- Media uploads should be served from a dedicated media service in production; Django's development media serving is enabled only when `DEBUG` is true.
