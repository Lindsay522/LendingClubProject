# React (`luna-app`) ↔ FastAPI integration

## Environment

```env
# luna-app/.env.development
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

Production (Vercel):

```env
VITE_API_URL=https://your-railway-or-render-url/api/v1
```

## API client sketch

```typescript
// src/api/client.ts
const BASE = import.meta.env.VITE_API_URL ?? "/api/v1";

export function getToken() {
  return sessionStorage.getItem("luna_access_token");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  const t = getToken();
  if (t) headers.set("Authorization", `Bearer ${t}`);
  const res = await fetch(`${BASE}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error((body as { detail?: string }).detail ?? res.statusText);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
```

## Auth flow

1. `POST /auth/register` with `{ email, password }`
2. `POST /auth/login` → `{ access_token }` → store in `sessionStorage`
3. Attach `Authorization: Bearer …` on all subsequent calls
4. `GET /auth/me` to hydrate profile

## Feature mapping

| Current (localStorage) | New endpoint |
|------------------------|--------------|
| Closet list/add | `GET/POST /closet` |
| Outfits | `GET/POST /outfits` |
| Sleep / sport / mood | `POST /wellness/sleep`, `/sport`, `/mood` |
| Calendar | `POST/GET /wellness/events` |
| Focus timer complete | `POST /wellness/focus-sessions` |
| Dashboard stats | `GET /analytics/summary` |
|Charts | `GET /analytics/trends` + Recharts |
| Suggestions | `GET /recommendations/outfits` etc. |

## CORS

Backend `CORS_ORIGINS` must include your Verc/GitHub Pages origin (see `.env.example`).
