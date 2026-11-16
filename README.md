# CyclePrep: Period Prep Tracker

CyclePrep is a period tracking web app for women who want a simple heads-up before
their period arrives, instead of a full medical tracking tool. It is built for
preparation: restocking supplies, preparing pain relief, and planning around exams
and other activities.

This repository currently contains **Phase 1: the Account Feature**, which the rest
of the system depends on.

## Technology stack

- **Language:** Python
- **Framework:** Django (full stack, using Django templates for the frontend)
- **Database:** Supabase (PostgreSQL)

## Account features

| Feature | What it does |
|---|---|
| Registration | Sign-up form with required fields, email format check, unique username and email, and password confirmation. Passwords are hashed by Django's built-in authentication. |
| Login / Logout | Log in with username and password. Invalid credentials show an error. Logging out ends the session. |
| Protected pages | Dashboards and profile pages require login. Logged-out users are sent to the login page. |
| Role-based dashboards | Each user is sent to the dashboard for their role after logging in. A user cannot open the other role's dashboard by typing its URL. |
| User profile | Users can view and update their own name, email, contact number, cycle type, and profile photo. Users can only see and edit their own profile. |

## User roles

| Role | How the account is created | Dashboard |
|---|---|---|
| **Member** | Through the registration form | Cycle overview cards (cycle logging and predictions come in the next phase) |
| **Admin** | With `python manage.py createsuperuser` | User totals, regular vs irregular counts, and the list of accounts |

## Setup

1. Clone the repository and open the project folder.

2. Create and activate a virtual environment, then install the requirements.

   ```bash
   python -m venv venv
   venv\Scripts\activate          # Windows
   # source venv/bin/activate     # macOS / Linux
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and fill in your own values. The database values
   come from Supabase (**Connect > Direct > Session pooler**).

   ```
   SECRET_KEY=your-generated-secret-key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   DB_NAME=postgres
   DB_USER=postgres.your-project-ref
   DB_PASSWORD=your-database-password
   DB_HOST=your-pooler-host.pooler.supabase.com
   DB_PORT=5432
   ```

   Generate a secret key with:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

4. Create the database tables, make an Admin account, and start the server.

   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. Open http://127.0.0.1:8000/ in a browser.

## Main pages

| URL | Page | Access |
|---|---|---|
| `/` | Home | Everyone |
| `/register/` | Registration | Logged-out users |
| `/login/` | Login | Logged-out users |
| `/dashboard/` | Redirects to the dashboard for the user's role | Logged-in users |
| `/dashboard/member/` | Member dashboard | Members only |
| `/dashboard/admin/` | Admin dashboard | Admins only |
| `/profile/` | View own profile | Logged-in users |
| `/profile/edit/` | Edit own profile | Logged-in users |

## Project structure

```
accounts/      Account feature: models, forms, views, role decorator, URLs
cycleprep/     Project settings and root URL configuration
templates/     Django templates (base layout, account pages, dashboards)
static/        CSS
```

## Security notes

- Database credentials and the secret key are stored in `.env`, which is listed in
  `.gitignore` and is never committed.
- `venv/`, `__pycache__/`, and uploaded files in `media/` are also excluded from the
  repository.
