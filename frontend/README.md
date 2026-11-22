# ArtGallery frontend

React 18 application powered by Vite.

## Commands

```bash
npm install
npm run dev
npm run lint
npm run build
```

## Environment

Create `.env` when the API is not available at its local default:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
# Optional separately deployed scanner:
# VITE_SCANNER_URL=https://scanner.example.com
```

The shared API client in `src/api.js` adds the bearer token to authenticated requests and normalizes the API base URL.
