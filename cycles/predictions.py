"""Cycle predictions for CyclePrep.

Regular cycles: estimate the next start date.
- With 2 or more logged periods, use the average of the recent cycle lengths.
- With only 1 logged period, use the typical 22 to 28 day range.

Irregular cycles: show the days since the last period and the likely phase.

These are simple estimates for preparation, not medical predictions.
"""
from dataclasses import dataclass
from datetime import date, timedelta

TYPICAL_MIN_DAYS = 22
TYPICAL_MAX_DAYS = 28
DEFAULT_CYCLE_DAYS = 28
REMINDER_DAYS_BEFORE = 3
RECENT_CYCLES = 6
# Gaps outside this range are ignored (usually a missed log)
MIN_VALID_GAP = 15
MAX_VALID_GAP = 60
# An ongoing log older than this is treated as a forgotten end date
MAX_ONGOING_DAYS = 10

PHASES = {
    'menstrual': ('Menstrual', 'Your period. Keep pads and pain relief nearby.'),
    'follicular': ('Follicular', 'After your period. Energy often picks up in this phase.'),
    'ovulation': ('Ovulation', 'Mid-cycle. Some people notice mild cramps or more discharge.'),
    'luteal': ('Luteal', 'The days before your period. Good time to restock supplies.'),
}


def cycle_lengths(logs):
    """Days between consecutive period start dates, oldest first."""
    starts = sorted(log.start_date for log in logs)
    gaps = [(later - earlier).days for earlier, later in zip(starts, starts[1:])]
    return [gap for gap in gaps if MIN_VALID_GAP <= gap <= MAX_VALID_GAP]


def average_cycle_length(logs):
    """Average of the most recent cycle lengths, or None without enough data."""
    lengths = cycle_lengths(logs)[-RECENT_CYCLES:]
    if not lengths:
        return None
    return round(sum(lengths) / len(lengths))


def _latest(logs):
    return max(logs, key=lambda log: log.start_date)


def _is_on_period(log, today):
    if log.end_date is not None:
        return log.start_date <= today <= log.end_date
    return (today - log.start_date).days < MAX_ONGOING_DAYS


@dataclass
class Prediction:
    last_start: date
    cycle_length: int
    uses_history: bool
    next_start: date
    window_start: date
    window_end: date
    days_until: int
    on_period: bool
    is_late: bool
    show_reminder: bool


def predict_next_period(logs, today):
    """Next-period estimate for a regular cycle. Returns None with no logs."""
    logs = list(logs)
    if not logs:
        return None

    latest = _latest(logs)
    average = average_cycle_length(logs)

    if average:
        cycle_length = average
        next_start = latest.start_date + timedelta(days=cycle_length)
        window_start = next_start - timedelta(days=2)
        window_end = next_start + timedelta(days=2)
    else:
        cycle_length = DEFAULT_CYCLE_DAYS
        next_start = latest.start_date + timedelta(days=cycle_length)
        window_start = latest.start_date + timedelta(days=TYPICAL_MIN_DAYS)
        window_end = latest.start_date + timedelta(days=TYPICAL_MAX_DAYS)

    on_period = _is_on_period(latest, today)
    reminder_from = window_start - timedelta(days=REMINDER_DAYS_BEFORE)

    return Prediction(
        last_start=latest.start_date,
        cycle_length=cycle_length,
        uses_history=bool(average),
        next_start=next_start,
        window_start=window_start,
        window_end=window_end,
        days_until=(next_start - today).days,
        on_period=on_period,
        is_late=not on_period and today > window_end,
        show_reminder=not on_period and reminder_from <= today <= window_end,
    )


@dataclass
class CycleStatus:
    last_start: date
    days_since: int
    months_since: int
    cycle_day: int
    cycle_length: int
    uses_history: bool
    on_period: bool
    missing_end_date: bool
    phase_key: str
    phase_name: str
    phase_note: str
    show_reminder: bool


def current_status(logs, today):
    """Days since the last period and the likely phase. Returns None with no logs."""
    logs = list(logs)
    if not logs:
        return None

    latest = _latest(logs)
    average = average_cycle_length(logs)
    cycle_length = average or DEFAULT_CYCLE_DAYS

    days_since = (today - latest.start_date).days
    cycle_day = days_since + 1
    on_period = _is_on_period(latest, today)
    ovulation_day = max(cycle_length - 14, 8)

    if on_period:
        phase_key = 'menstrual'
    elif cycle_day < ovulation_day - 1:
        phase_key = 'follicular'
    elif cycle_day <= ovulation_day + 1:
        phase_key = 'ovulation'
    else:
        phase_key = 'luteal'

    phase_name, phase_note = PHASES[phase_key]
    if phase_key == 'luteal' and cycle_day > cycle_length:
        phase_note = 'You are past your usual cycle length. Your period could start any day.'

    return CycleStatus(
        last_start=latest.start_date,
        days_since=days_since,
        months_since=days_since // 30,
        cycle_day=cycle_day,
        cycle_length=cycle_length,
        uses_history=bool(average),
        on_period=on_period,
        missing_end_date=latest.end_date is None and not on_period,
        phase_key=phase_key,
        phase_name=phase_name,
        phase_note=phase_note,
        show_reminder=(
            bool(average)
            and not on_period
            and cycle_day >= cycle_length - REMINDER_DAYS_BEFORE
        ),
    )
