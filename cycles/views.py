from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import role_required
from accounts.models import Profile

from .forms import CycleLogForm
from .models import CycleLog


@role_required(Profile.Role.MEMBER)
def cycle_list(request):
    """Read: the member's own cycle logs, newest first."""
    logs = request.user.cycle_logs.prefetch_related('symptoms')
    return render(request, 'cycles/cycle_list.html', {'logs': logs})


@role_required(Profile.Role.MEMBER)
def cycle_create(request):
    """Create: log a new period. The start date defaults to today."""
    if request.method == 'POST':
        form = CycleLogForm(request.POST, user=request.user)
        if form.is_valid():
            log = form.save(commit=False)
            log.user = request.user
            log.save()
            form.save_m2m()
            messages.success(request, 'Your period was logged.')
            return redirect('cycle_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CycleLogForm(user=request.user, initial={'start_date': timezone.localdate()})

    return render(request, 'cycles/cycle_form.html', {'form': form, 'is_edit': False})


@role_required(Profile.Role.MEMBER)
def cycle_update(request, pk):
    """Update: edit one of the member's own logs. Other users' logs return 404."""
    log = get_object_or_404(CycleLog, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CycleLogForm(request.POST, instance=log, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your cycle log was updated.')
            return redirect('cycle_list')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CycleLogForm(instance=log, user=request.user)

    return render(
        request, 'cycles/cycle_form.html', {'form': form, 'is_edit': True, 'log': log}
    )


@role_required(Profile.Role.MEMBER)
def cycle_delete(request, pk):
    """Delete: remove one of the member's own logs after confirming."""
    log = get_object_or_404(CycleLog, pk=pk, user=request.user)

    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Your cycle log was deleted.')
        return redirect('cycle_list')

    return render(request, 'cycles/cycle_confirm_delete.html', {'log': log})


@role_required(Profile.Role.ADMIN)
def cycle_admin_list(request):
    """Read-only list of every member's logs, for Admins."""
    query = request.GET.get('q', '').strip()
    logs = CycleLog.objects.select_related('user').prefetch_related('symptoms')
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )
    return render(request, 'cycles/admin_cycle_list.html', {'logs': logs, 'query': query})
