# CyclePrep: Period Prep Tracker

A simple period tracking web app that predicts the next cycle and reminds users to prepare a few days ahead.

**Stack:** Python · Django (full stack, Django templates) · Supabase (PostgreSQL)

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your values. Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Then run:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
