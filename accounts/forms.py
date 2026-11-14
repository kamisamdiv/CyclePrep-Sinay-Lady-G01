from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


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
