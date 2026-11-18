from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.utils import timezone

from cycles.models import CycleLog
from cycles.predictions import average_cycle_length, current_status, predict_next_period

from .decorators import get_profile, role_required
from .forms import ProfileUpdateForm, RegistrationForm, UserUpdateForm
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
    profile = get_profile(request.user)
    today = timezone.localdate()
    logs = list(request.user.cycle_logs.all())

    context = {
        'profile': profile,
        'today': today,
        'recent_logs': logs[:3],
        'log_count': len(logs),
        'ongoing_log': next((log for log in logs if log.end_date is None), None),
        'average_length': average_cycle_length(logs),
    }
    if profile.cycle_type == Profile.CycleType.REGULAR:
        context['prediction'] = predict_next_period(logs, today)
    else:
        context['status'] = current_status(logs, today)

    return render(request, 'dashboards/member.html', context)


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
        'total_logs': CycleLog.objects.count(),
        'members_logging': CycleLog.objects.values('user').distinct().count(),
        'ongoing_logs': CycleLog.objects.filter(end_date__isnull=True).count(),
        'average_cycle': _average_cycle_for_all_members(),
    }
    return render(request, 'dashboards/admin.html', context)


@login_required
def profile(request):
    """Show the logged-in user's own profile.

    There is no user id in the URL, so nobody can open another user's profile.
    """
    return render(request, 'accounts/profile.html', {'profile': get_profile(request.user)})


@login_required
def profile_edit(request):
    """Let the logged-in user update their own profile."""
    user_profile = get_profile(request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated.')
            return redirect('profile')
        messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=user_profile)

    return render(
        request,
        'accounts/profile_edit.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )


def _average_cycle_for_all_members():
    """Average cycle length across members who have at least 2 logs."""
    logs_by_user = {}
    for log in CycleLog.objects.only('user_id', 'start_date'):
        logs_by_user.setdefault(log.user_id, []).append(log)

    averages = [average_cycle_length(logs) for logs in logs_by_user.values()]
    averages = [value for value in averages if value]
    if not averages:
        return None
    return round(sum(averages) / len(averages))
