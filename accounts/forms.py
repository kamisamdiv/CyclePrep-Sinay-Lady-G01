import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.files.uploadedfile import UploadedFile

from .models import Profile

MAX_PHOTO_SIZE = 2 * 1024 * 1024  # 2 MB


class RegistrationForm(UserCreationForm):
    """Sign-up form for new Members.

    UserCreationForm already checks that the username is unique, that the
    two passwords match, and it hashes the password before saving.
    """

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    cycle_type = forms.ChoiceField(
        choices=Profile.CycleType.choices,
        label='Is your cycle regular or irregular?',
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Plain-text help, so the template never needs |safe
        self.fields['password1'].help_text = (
            'At least 8 characters. Do not use only numbers, a common password, '
            'or something too similar to your username or name.'
        )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()  # the signal creates the Profile here
            user.profile.cycle_type = self.cleaned_data['cycle_type']
            user.profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    """Edit the name and email stored on the User account."""

    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        taken = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if taken.exists():
            raise forms.ValidationError('Another account already uses this email.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Edit the extra profile details (contact number, cycle type, photo)."""

    class Meta:
        model = Profile
        fields = ('contact_number', 'cycle_type', 'profile_photo')
        labels = {
            'cycle_type': 'Is your cycle regular or irregular?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cycle type only applies to Members, so hide it for Admins
        if self.instance and self.instance.role == Profile.Role.ADMIN:
            self.fields.pop('cycle_type')

    def clean_contact_number(self):
        number = self.cleaned_data.get('contact_number', '').strip()
        if number and not re.fullmatch(r'\+?[0-9][0-9 \-]{6,18}', number):
            raise forms.ValidationError(
                'Enter a valid contact number, for example 09171234567 or +63 917 123 4567.'
            )
        return number

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        # Only check files uploaded in this request (not the saved one)
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_SIZE:
            raise forms.ValidationError('The photo must be 2 MB or smaller.')
        return photo
