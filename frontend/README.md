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

The shared API client in `src/api.js` sends the HttpOnly gallery session cookie with credentialed requests and obtains a masked CSRF token from the API before unsafe requests. Configure the API's CORS and CSRF trusted origins to include the exact frontend origin.
