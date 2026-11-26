from django.core.management.base import BaseCommand
from django.utils import timezone

from cycles.reminders import send_due_reminders


class Command(BaseCommand):
    help = 'Email the period heads-up to every member who is due one today.'

    def handle(self, *args, **options):
        sent = send_due_reminders(timezone.localdate())
        self.stdout.write(self.style.SUCCESS(f'Sent {sent} reminder email(s).'))
