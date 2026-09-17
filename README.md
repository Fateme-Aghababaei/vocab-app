# Memento

Learn English words that stick. Save vocabulary, generate definitions and examples
with Gemini, and practice with flashcards scheduled around what you remember.
Each account has its own vocabulary library.

**Stack:** Vue 3, TypeScript, Vite, PrimeVue, Tailwind CSS, and Pinia in `frontend/`;
Django REST Framework, SQLite, and Gemini in `backend/`.

## Run locally

Start the backend:

```bash
# Backend Setup
cd backend
python3 -m venv .venv
source .venv/bin/activate                            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # Windows: copy .env.example .env (first setup only)
python manage.py migrate
python manage.py import_vocabulary --file=words.csv  # Seed initial vocabulary dictionary into database
python manage.py runserver
```

Set `GEMINI_API_KEYS` in `backend/.env` to enable AI generation. See the template
for model and timeout settings. On Windows, activate with `.venv\Scripts\activate`.

In another terminal, start the frontend:

```bash
cd frontend
npm install
cp .env.example .env  # first setup only; keep existing settings
npm run dev
```

Open `http://localhost:5173`. Frontend API requests are proxied to Django at
`http://127.0.0.1:8000`. Create an account, add words, and rate reviews with
**Again**, **Hard**, **Good**, or **Easy** to adjust their next review date.

## Configuration

Local `.env` files are ignored by Git; `.env.example` files are shared templates.
Never put secrets in frontend variables—they are included in the public build.

Set these in `frontend/.env` or your hosting provider’s build environment:

| Variable | Purpose |
| --- | --- |
| `VITE_SITE_URL` | Public origin, e.g. `https://memento.ir`; generates canonical links and a sitemap |
| `VITE_CONTACT_EMAIL` | Footer email address |
| `VITE_INSTAGRAM_URL`, `VITE_TELEGRAM_URL`, `VITE_GITHUB_URL` | Footer social links using HTTPS |

Empty contact settings use placeholder links. Restart the dev server or rebuild
after changing environment settings.

## Build and deploy

Run from `frontend/`:

```bash
npm run build       # type-check and build into dist/
npm run preview     # preview the production build locally
npm run lint        # check code style
```

- Serve `frontend/dist/` at the root of an HTTPS site and proxy `/api/` to Django.
  Use a production Django server, set `DJANGO_DEBUG=False`, a private
  `DJANGO_SECRET_KEY`, and appropriate `DJANGO_ALLOWED_HOSTS`; run migrations.
- Serve static files first, then return `index.html` for frontend routes.
  Keep `/api/` and `/admin/` out of the frontend fallback.
- Revalidate `index.html` and `manifest.webmanifest`; serve `sw.js` as JavaScript
  with `Cache-Control: no-cache`. Hashed assets can use immutable caching.
- `/` is the public landing page; `/app` opens the authenticated dashboard.
  Submit `/sitemap.xml` to Google Search Console after deployment; indexing takes time.

## Install the app

Use **Install app**, or on iPhone choose Safari → Share → Add to Home Screen.
Installation requires HTTPS (or localhost). The service worker runs in production
and provides an offline notice; accounts, vocabulary, and reviews require internet.
