from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """Extra information for each user account (one profile per user)."""

    class Role(models.TextChoices):
        MEMBER = 'member', 'Member'
        ADMIN = 'admin', 'Admin'

    class CycleType(models.TextChoices):
        REGULAR = 'regular', 'Regular'
        IRREGULAR = 'irregular', 'Irregular'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    cycle_type = models.CharField(
        max_length=10, choices=CycleType.choices, default=CycleType.REGULAR
    )
    contact_number = models.CharField(max_length=20, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    # Expected start date of the period we last emailed a heads-up about,
    # so the reminder command never sends the same reminder twice.
    last_reminder_for = models.DateField(null=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_member(self):
        return self.role == self.Role.MEMBER
