# Step-by-step implementation plan

## Phase 0 — Bootstrap (done in `luna-platform/backend`)

- [x] FastAPI app layout, config, SQLite, SQLAlchemy models
- [x] JWT register/login + Bearer auth dependency
- [x] REST routes: closet, outfits, wellness logs, analytics, recommendations
- [x] Pandas analytics + rule-based recommender

## Phase 1 — Frontend migration (`luna-app`)

1. Add `VITE_API_URL` and `src/api/client.ts` (axios/fetch + `Authorization` header).
2. Replace `LunaProvider` localStorage with:
   - Login/register screens
   - TanStack Query (`useQuery` / `useMutation`) keyed by `userId`
3. Mirror existing screens; add **Analytics** route (charts: Recharts or Chart.js).
4. Call `POST /wellness/outfit-worn` when user marks an outfit “worn today”.
5. Call `POST /wellness/focus-sessions` when focus timer completes.

## Phase 2 — Research narrative

1. **IRB-style data section** in README: what is collected, retention, opt-in.
2. Export anonymized aggregates (CSV) from `/analytics/*` for a paper appendix.
3. Ablations: disable one recommender signal, show drop in NDCG@5 or user study Likert.

## Phase 3 — Production hardening

- Alembic migrations; Postgres on Railway/Render
- Refresh tokens, password reset email
- Rate limiting (slowapi), structured logging (structlog)
- Pytest + httpx AsyncClient for API tests

## Phase 4 — ML upgrade (optional thesis chunk)

- Learn weights on “outfit chosen vs shown” with logistic regression (scikit-learn).
- Or session-based matrix factorization on outfit co-occurrence from wear logs.
