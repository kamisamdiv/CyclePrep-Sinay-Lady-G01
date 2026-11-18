from django import forms
from django.utils import timezone

from .models import CycleLog

MAX_PERIOD_DAYS = 15


class CycleLogForm(forms.ModelForm):
    """Log or edit one period.

    Business rules:
    - dates cannot be in the future
    - the end date cannot be before the start date
    - a period cannot be longer than 15 days
    - a log cannot overlap another log of the same member
    - only one ongoing period (no end date) at a time
    """

    class Meta:
        model = CycleLog
        fields = ('start_date', 'end_date', 'symptoms', 'notes')
        labels = {
            'start_date': 'Start date',
            'end_date': 'End date (optional)',
            'symptoms': 'Symptoms (optional)',
            'notes': 'Notes (optional)',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'end_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'symptoms': forms.CheckboxSelectMultiple,
            'notes': forms.Textarea(
                attrs={'rows': 3, 'maxlength': 500, 'placeholder': 'Anything to remember?'}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        today = timezone.localdate().isoformat()
        self.fields['start_date'].widget.attrs['max'] = today
        self.fields['end_date'].widget.attrs['max'] = today

    def clean_start_date(self):
        start = self.cleaned_data['start_date']
        if start > timezone.localdate():
            raise forms.ValidationError('The start date cannot be in the future.')
        return start

    def clean_end_date(self):
        end = self.cleaned_data.get('end_date')
        if end and end > timezone.localdate():
            raise forms.ValidationError(
                'The end date cannot be in the future. Leave it blank if your period is ongoing.'
            )
        return end

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if start and end:
            if end < start:
                self.add_error('end_date', 'The end date cannot be before the start date.')
            elif (end - start).days + 1 > MAX_PERIOD_DAYS:
                self.add_error(
                    'end_date',
                    f'A period cannot be longer than {MAX_PERIOD_DAYS} days. Please check the dates.',
                )

        if start and self.user is not None and not self.errors:
            self._check_other_logs(start, end)

        return cleaned

    def _check_other_logs(self, start, end):
        today = timezone.localdate()
        others = CycleLog.objects.filter(user=self.user)
        if self.instance.pk:
            others = others.exclude(pk=self.instance.pk)

        if end is None:
            ongoing = others.filter(end_date__isnull=True).first()
            if ongoing:
                raise forms.ValidationError(
                    'You already have an ongoing period that started on '
                    f'{ongoing.start_date:%B %d, %Y}. Add its end date first.'
                )

        new_end = end or today
        for log in others:
            log_end = log.end_date or today
            if log.start_date <= new_end and start <= log_end:
                raise forms.ValidationError(
                    'These dates overlap with the period you logged on '
                    f'{log.start_date:%B %d, %Y}.'
                )
