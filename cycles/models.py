from django.conf import settings
from django.db import models

DEFAULT_SYMPTOMS = [
    'Cramps',
    'Headache',
    'Bloating',
    'Fatigue',
    'Back pain',
    'Mood changes',
    'Acne',
    'Breast tenderness',
]


class Symptom(models.Model):
    """A symptom a member can tag on a cycle log (e.g. Cramps, Headache)."""

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CycleLog(models.Model):
    """One logged period, owned by the member who created it."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cycle_logs',
    )
    start_date = models.DateField()
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text='Leave blank if your period is still ongoing.',
    )
    symptoms = models.ManyToManyField(Symptom, blank=True, related_name='cycle_logs')
    notes = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        end = self.end_date or 'ongoing'
        return f'{self.user.username}: {self.start_date} to {end}'

    @property
    def is_ongoing(self):
        return self.end_date is None

    @property
    def period_length(self):
        """Number of days the period lasted (start and end day included)."""
        if self.end_date is None:
            return None
        return (self.end_date - self.start_date).days + 1
