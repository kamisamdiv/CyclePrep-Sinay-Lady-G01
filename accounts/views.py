from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .decorators import get_profile, role_required
from .forms import RegistrationForm
from .models import Profile


def home(request):
    """Public landing page."""
    return render(request, 'home.html')


def register(request):
    """Create a new Member account."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. You can now log in.')
            return redirect('login')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


class UserLoginView(LoginView):
    """Log in with username and password (Django's built-in authentication)."""

    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Welcome back, {user.first_name or user.username}!')
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """Log out (POST only) and end the session."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, 'You have been logged out.')
        return response


@login_required
def dashboard_redirect(request):
    """Send each user to the dashboard for their role."""
    if get_profile(request.user).role == Profile.Role.ADMIN:
        return redirect('admin_dashboard')
    return redirect('member_dashboard')


@role_required(Profile.Role.MEMBER)
def member_dashboard(request):
    return render(request, 'dashboards/member.html', {'profile': get_profile(request.user)})


@role_required(Profile.Role.ADMIN)
def admin_dashboard(request):
    members = Profile.objects.filter(role=Profile.Role.MEMBER)
    context = {
        'total_users': User.objects.count(),
        'member_count': members.count(),
        'admin_count': Profile.objects.filter(role=Profile.Role.ADMIN).count(),
        'regular_count': members.filter(cycle_type=Profile.CycleType.REGULAR).count(),
        'irregular_count': members.filter(cycle_type=Profile.CycleType.IRREGULAR).count(),
        'users': User.objects.select_related('profile').order_by('-date_joined'),
    }
    return render(request, 'dashboards/admin.html', context)
