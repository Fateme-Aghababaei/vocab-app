# Vocab — a flashcard-based vocabulary learner

A minimal, focused app for saving new English words and reviewing them with
spaced repetition. Add a word, let Gemini Flash draft the definition,
examples, usage notes, collocations, difficulty, and categories, edit
anything you like, then review it as a flashcard on a schedule that adapts
to how well you remember it.

**Stack**
- Frontend: Vue 3 + TypeScript, PrimeVue (Aura theme, custom preset), Tailwind CSS, Pinia, Vite
- Backend: Django + Django REST Framework, SQLite, Gemini Flash API

## Project layout

```
backend/     Django project (API only, no server-rendered pages)
frontend/    Vue 3 SPA
```

## 1. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env and set GEMINI_API_KEY
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin/
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api/`. Get a Gemini API key at
https://aistudio.google.com/app/apikey — without it, word creation still
works, but the "Generate with AI" step will show an error and fall back to
manual entry.

### Key endpoints

| Method | Path                         | Purpose                                   |
|--------|------------------------------|--------------------------------------------|
| POST   | `/api/auth/register/`        | Create an account (`email`, `password`, `name`), returns a token |
| POST   | `/api/auth/login/`           | Log in (`email`, `password`), returns a token |
| POST   | `/api/auth/logout/`          | Invalidate the current token |
| GET    | `/api/auth/me/`              | Current user's profile |
| POST   | `/api/words/generate/`       | Ask Gemini to draft info for a word (not saved) |
| GET    | `/api/words/`                | List the current user's words (`?search=`, `?category=`, `?difficulty=`, `?due=true`) |
| POST   | `/api/words/`                | Save a new word |
| GET    | `/api/words/:id/`            | Word detail |
| PATCH  | `/api/words/:id/`            | Edit a word |
| DELETE | `/api/words/:id/`            | Delete a word |
| GET    | `/api/words/due/`            | Words due for review right now |
| POST   | `/api/words/:id/review/`     | Submit a review (`{"quality": 0-3}`), reschedules the word |
| GET    | `/api/words/categories/`     | Suggested + in-use categories |
| GET    | `/api/stats/`                | Dashboard counters |

Every `/api/words/*` and `/api/stats/` endpoint requires an `Authorization: Token <key>` header and only ever sees/affects the requesting user's own words — enforced in `words/views.py` via `get_queryset()`, not just in the frontend.

## 2. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173` and proxies `/api` to `http://127.0.0.1:8000`
(see `vite.config.ts`). Run the backend first.

`npm run build` produces a static bundle in `frontend/dist/` you can serve
from any static host or from Django's `staticfiles` if you prefer a single
deployment.

## How review scheduling works

Each word carries its own `ease_factor`, `interval_days`, and
`next_review_date` (see `backend/words/srs.py`). It's an SM-2-style
algorithm (the same family used by Anki/SuperMemo), adapted for a 4-button
review UI:

- **Again** — forgotten. Resets the learning streak and resurfaces the word
  the same day.
- **Hard** — remembered with effort. Small interval increase, ease factor
  nudged down.
- **Good** — remembered comfortably. Interval grows by the ease factor.
- **Easy** — remembered instantly. Interval grows faster, ease factor nudged
  up.

A word's declared **difficulty** (beginner/intermediate/advanced) only sets
its *starting* ease factor — harder words start on a slightly tighter
schedule — after that, your own review history drives everything.

The frontend also shows a rough preview of the next interval next to each
button (`frontend/src/utils/srsPreview.ts`), purely as a UX hint; the
backend is always the source of truth for actual scheduling.

## Design notes

- Palette: white/warm-neutral (`stone`) surfaces throughout, with
  `#EF476F` (pink) reserved for primary actions, active nav state, and
  "important" signals (e.g. Advanced difficulty, the due-today hero), and
  `#FFD166` (yellow) used for highlights — badges, progress fills, the
  "reviewed today" tile, collocation chips.
- Type: **Fraunces** (a warm display serif) for the word itself and
  headings, **Inter** for everything else — the serif gives saved words a
  bit of "dictionary entry" character without slowing down the UI.
- The flashcard is a real flip (`FlashCard.vue`), not just a reveal, and
  reduced-motion is respected.
- No user accounts — this is intentionally a single-user, local-first study
  tool. Adding auth (e.g. DRF token auth + a login view) would be the
  natural next step if you want multiple learners.

## Auth

Accounts use email + password with DRF token authentication (`accounts/`
app). Registering or logging in returns a token that the frontend stores in
`localStorage` and sends as `Authorization: Token <key>` on every request
(see `frontend/src/services/api.ts`). A 401 anywhere clears the stored token
and bounces the user to `/login`.

Each `Word` belongs to exactly one user (`words/models.py`), and every list,
create, update, delete, review, and stats query is scoped to
`request.user` server-side — not just hidden in the UI. Two users can save
the same word text; word text only needs to be unique per user.

The router (`frontend/src/router/index.ts`) guards every route except
`/login` and `/signup`, redirecting unauthenticated visitors to `/login`
(and back afterwards, via a `next` query param), and redirecting already
logged-in users away from the auth pages.

## Install on your phone (PWA)

The production frontend includes a web app manifest, Android and Apple home-screen
icons, standalone display mode, installation help, and a service worker with a
public offline page. Your words, account, reviews, and AI generation still require
an internet connection; API responses are never cached by the service worker.

1. Run `npm run build` in `frontend`.
2. Serve `frontend/dist` at the root of an **HTTPS** website. Route `/api/` to
   Django on the same origin, and configure `DJANGO_ALLOWED_HOSTS` for the host
   forwarded to Django. Keep the Gemini key on the backend.
3. Serve actual static files before the SPA fallback. Other frontend routes
   (such as `/library`) should return `index.html`. Serve `sw.js` with a JavaScript
   content type and `Cache-Control: no-cache`; serve `index.html` and
   `manifest.webmanifest` with revalidation. Hashed `/assets/` files can use
   long-lived immutable caching. Do not rewrite `/api/` requests to the SPA.
4. On iPhone, visit the HTTPS site in Safari and choose **Share → Add to Home
   Screen** (enable **Open as Web App** if offered). On Android Chrome, use the
   in-app install button when available, or **⋮ → Install app / Add to Home screen**.

For a local production check, run `npm run preview` after building, with Django
running. Vite preview inherits the development API proxy. Open the localhost URL
on the computer and inspect Application → Manifest and Service Workers in browser
devtools. Service-worker registration is intentionally disabled during `npm run dev`.
An HTTP LAN URL such as `http://192.168.x.x:5173` is not sufficient for full PWA
installation on a phone: use a trusted HTTPS deployment.

After an initial online visit, close and reopen the app once so the worker controls
it, then disconnect and reopen to check the offline screen. Reconnect and tap
**Try again** to return. Workers update on subsequent visits and activate after
older app windows close, avoiding a forced refresh during word editing. When
changing `offline.html`, bump the cache version in `public/sw.js`.

Icon assets can be regenerated with `python3 frontend/scripts/generate-icons.py`.


### Study languages

Choose an initial study language at signup. The **I'm learning** selector above
each page lets you switch between your languages or use **Add language** to add
another one. Preferences are saved to your account. Save drafts and edits before
switching languages.

Each language has its own word library, review queue, categories, and statistics.
The same spelling can be saved once in each language. Existing words belong to
English, with their pronunciation and review history preserved. AI-generated
examples, collocations, and IPA follow the study language; the interface,
definitions, and usage explanations remain in English.

Apply backend migrations when updating: `python manage.py migrate` from `backend`
with the virtual environment activated. Supported languages are listed in
`backend/accounts/languages.py`. The API accepts `X-Study-Language` for vocabulary
requests, validates it against the user's languages, and otherwise uses the
account's saved active language.
