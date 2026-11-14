from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm


def home(request):
    """Public landing page."""
    return render(request, 'home.html')


def register(request):
    """Create a new Member account."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request, f'Account created successfully. Welcome, {user.first_name}!'
            )
            return redirect('home')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})
