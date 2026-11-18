"""Tests for the prediction logic. They do not need the database.

Run with: python manage.py test cycles
"""
from datetime import date, timedelta
from types import SimpleNamespace

from django.test import SimpleTestCase

from .predictions import (
    average_cycle_length,
    current_status,
    cycle_lengths,
    predict_next_period,
)


def log(start, end=None):
    return SimpleNamespace(start_date=start, end_date=end)


class CycleLengthTests(SimpleTestCase):
    def test_lengths_between_starts(self):
        logs = [log(date(2026, 8, 1)), log(date(2026, 8, 29)), log(date(2026, 9, 28))]
        self.assertEqual(cycle_lengths(logs), [28, 30])
        self.assertEqual(average_cycle_length(logs), 29)

    def test_ignores_unrealistic_gaps(self):
        logs = [log(date(2026, 1, 1)), log(date(2026, 6, 1))]
        self.assertEqual(cycle_lengths(logs), [])
        self.assertIsNone(average_cycle_length(logs))


class RegularPredictionTests(SimpleTestCase):
    def test_no_logs(self):
        self.assertIsNone(predict_next_period([], date(2026, 11, 18)))

    def test_one_log_uses_typical_range(self):
        start = date(2026, 11, 1)
        result = predict_next_period([log(start, start + timedelta(days=4))], date(2026, 11, 10))
        self.assertFalse(result.uses_history)
        self.assertEqual(result.window_start, start + timedelta(days=22))
        self.assertEqual(result.window_end, start + timedelta(days=28))
        self.assertEqual(result.next_start, start + timedelta(days=28))

    def test_average_from_history(self):
        logs = [
            log(date(2026, 9, 1), date(2026, 9, 5)),
            log(date(2026, 9, 27), date(2026, 10, 1)),
            log(date(2026, 10, 23), date(2026, 10, 27)),
        ]
        result = predict_next_period(logs, date(2026, 11, 1))
        self.assertTrue(result.uses_history)
        self.assertEqual(result.cycle_length, 26)
        self.assertEqual(result.next_start, date(2026, 11, 18))

    def test_reminder_three_days_before_window(self):
        start = date(2026, 10, 1)
        logs = [log(start, start + timedelta(days=4))]
        window_start = start + timedelta(days=22)
        self.assertFalse(predict_next_period(logs, window_start - timedelta(days=4)).show_reminder)
        self.assertTrue(predict_next_period(logs, window_start - timedelta(days=3)).show_reminder)

    def test_late_after_window(self):
        start = date(2026, 9, 1)
        result = predict_next_period([log(start, start + timedelta(days=4))], date(2026, 10, 15))
        self.assertTrue(result.is_late)


class IrregularStatusTests(SimpleTestCase):
    def test_on_period_is_menstrual(self):
        start = date(2026, 11, 15)
        status = current_status([log(start)], date(2026, 11, 17))
        self.assertTrue(status.on_period)
        self.assertEqual(status.phase_key, 'menstrual')

    def test_phases_for_default_cycle(self):
        start = date(2026, 10, 1)
        logs = [log(start, start + timedelta(days=4))]
        self.assertEqual(current_status(logs, start + timedelta(days=7)).phase_key, 'follicular')
        self.assertEqual(current_status(logs, start + timedelta(days=13)).phase_key, 'ovulation')
        self.assertEqual(current_status(logs, start + timedelta(days=20)).phase_key, 'luteal')

    def test_days_and_months_since(self):
        start = date(2026, 8, 1)
        status = current_status([log(start, start + timedelta(days=4))], date(2026, 10, 5))
        self.assertEqual(status.days_since, 65)
        self.assertEqual(status.months_since, 2)
