# CyclePrep: Period Prep Tracker

CyclePrep is a period tracking web app for women who want a simple heads-up before
their period arrives, instead of a full medical tracking tool. It is built for
preparation: restocking supplies, preparing pain relief, and planning around exams
and other activities.

Members can say whether their cycle is **regular** or **irregular**:

- **Regular:** CyclePrep estimates the next start date and shows a heads-up
  3 days before the expected window.
- **Irregular:** CyclePrep shows the days (and months) since the last period and
  the likely current phase (menstrual, follicular, ovulation, or luteal).

## Increments

| Increment | Contents |
|---|---|
| Project Development 1 | Account feature: registration, login/logout, role-based dashboards, profile |
| Project Development 2 | Core feature: cycle logging and prediction (vertical slice) |

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

## Core feature: Cycle Logging and Prediction

| Part | What it does |
|---|---|
| Log a period (Create) | Members log a start date (defaults to today), an optional end date, symptoms, and notes. |
| My cycle logs (Read) | Members see their own logs with period length and cycle length. |
| Edit a log (Update) | Members correct dates or add the end date when the period ends. |
| Delete a log (Delete) | Members delete one of their own logs after a confirmation page. |
| Predictions | Regular: next start date and window, with a 3-day reminder on the dashboard. Irregular: days since last period and likely phase. |
| Admin view | Admins see read-only cycle logs for all members and cycle statistics on their dashboard. |

**Validation and business rules**

- The start date is required, and dates cannot be in the future.
- The end date cannot be before the start date.
- A period cannot be longer than 15 days.
- A log cannot overlap another log of the same member.
- Only one ongoing period (no end date) is allowed at a time.
- Members can only open, edit, or delete their own logs (other users' logs return 404).

**Prediction rules**

- With 1 logged period, the next period is expected 22 to 28 days after the last start.
- With 2 or more, CyclePrep uses the average of the last 6 cycle lengths (15 to 60 day
  gaps only), with a window of 2 days on either side.
- Phases use the average cycle length (or 28 days): ovulation is about 14 days before
  the next period.

**Data model**

| Model | Key fields | Relationships |
|---|---|---|
| Profile | role, cycle_type, contact_number, profile_photo | OneToOne → User |
| CycleLog | start_date, end_date, notes, created_at | ForeignKey → User, ManyToMany → Symptom |
| Symptom | name | ManyToMany ← CycleLog |

## User roles

| Role | How the account is created | Dashboard |
|---|---|---|
| **Member** | Through the registration form | Next-period prediction or phase, reminders, logging, recent logs |
| **Admin** | With `python manage.py createsuperuser` | User and cycle statistics, list of accounts, read-only cycle logs |

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

   `migrate` also adds the default symptom choices (Cramps, Headache, and others).

5. Open http://127.0.0.1:8000/ in a browser.

6. Optional: run the prediction tests (they do not need the database).

   ```bash
   python manage.py test cycles
   ```

## Branching strategy

- `main`: stable code only, updated through pull requests from `develop`
- `develop`: integration branch
- `feature/<name>`: one branch per feature, merged into `develop` with a pull request
  (`feature/cycle-logging`, `feature/cycle-prediction`)

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
| `/cycles/` | My cycle logs | Members only |
| `/cycles/new/` | Log a period | Members only |
| `/cycles/<id>/edit/` | Edit own log | Members only (owner) |
| `/cycles/<id>/delete/` | Delete own log | Members only (owner) |
| `/cycles/all/` | All cycle logs (read-only) | Admins only |

## Project structure

```
accounts/      Account feature: models, forms, views, role decorator, URLs
cycles/        Core feature: CycleLog and Symptom models, form, views, predictions, tests
cycleprep/     Project settings and root URL configuration
templates/     Django templates (base layout, account pages, dashboards, cycle pages)
static/        CSS
docs/          Project reports (PD2 completion report)
```

## Security notes

- Database credentials and the secret key are stored in `.env`, which is listed in
  `.gitignore` and is never committed.
- `venv/`, `__pycache__/`, and uploaded files in `media/` are also excluded from the
  repository.
