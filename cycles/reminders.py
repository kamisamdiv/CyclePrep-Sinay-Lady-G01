"""Email heads-up reminders (fixes PD2 issue ISS-01).

The dashboard banner only shows when a member opens the dashboard. This
module sends the same heads-up by email. Run it once a day with:

    python manage.py send_reminders

Each reminder is sent only once per expected period, because the expected
start date is saved on the member's profile (Profile.last_reminder_for).
"""
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from accounts.models import Profile

from .predictions import current_status, predict_next_period


def expected_start_to_remind(profile, logs, today):
    """Expected start date to remind this member about today, or None."""
    if profile.cycle_type == Profile.CycleType.REGULAR:
        prediction = predict_next_period(logs, today)
        if prediction and prediction.show_reminder:
            return prediction.next_start
        return None

    status = current_status(logs, today)
    if status and status.show_reminder:
        return status.last_start + timedelta(days=status.cycle_length)
    return None


def _message(user, expected):
    name = user.first_name or user.username
    subject = 'CyclePrep heads-up: your period may start soon'
    body = (
        f'Hi {name},\n\n'
        f'Based on your logged periods, your next period is expected around '
        f'{expected:%B %d, %Y}.\n\n'
        'Restock pads or tampons, pack pain relief, and plan around exams or long outings.\n\n'
        'This is an estimate for planning ahead, not medical advice.\n'
        '- CyclePrep'
    )
    return subject, body


def send_due_reminders(today):
    """Email every member who is due a heads-up today. Returns the number sent."""
    profiles = (
        Profile.objects.filter(role=Profile.Role.MEMBER, user__is_active=True)
        .exclude(user__email='')
        .select_related('user')
        .prefetch_related('user__cycle_logs')
    )

    sent = 0
    for profile in profiles:
        logs = list(profile.user.cycle_logs.all())
        expected = expected_start_to_remind(profile, logs, today)
        if expected is None or profile.last_reminder_for == expected:
            continue

        subject, body = _message(profile.user, expected)
        with transaction.atomic():
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [profile.user.email],
                fail_silently=False,
            )
            profile.last_reminder_for = expected
            profile.save(update_fields=['last_reminder_for', 'updated_at'])
        sent += 1
    return sent
