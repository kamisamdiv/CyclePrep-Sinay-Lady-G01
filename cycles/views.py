from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from accounts.decorators import role_required
from accounts.models import Profile

from .forms import CycleLogForm
from .models import CycleLog
from .predictions import average_cycle_length

MAX_SEARCH_LENGTH = 100
SAVE_CONFLICT_MESSAGE = (
    'This log could not be saved because it conflicts with another of your logs. '
    'Please check the dates.'
)


def _lock_member(user):
    """Lock the member's row until the transaction ends.

    Two saves for the same member (for example a double-clicked Save button
    in two tabs) then run one after the other, so the overlap check in
    CycleLogForm always sees the other log.
    """
    get_user_model().objects.select_for_update().get(pk=user.pk)


@require_GET
@role_required(Profile.Role.MEMBER)
def cycle_list(request):
    """Read: the member's own cycle logs, newest first."""
    logs = list(request.user.cycle_logs.prefetch_related('symptoms'))
    # Cycle length = days from this start date to the next logged start date
    for newer, older in zip(logs, logs[1:]):
        older.cycle_length = (newer.start_date - older.start_date).days
    return render(
        request,
        'cycles/cycle_list.html',
        {'logs': logs, 'average_length': average_cycle_length(logs)},
    )


@require_http_methods(['GET', 'POST'])
@role_required(Profile.Role.MEMBER)
def cycle_create(request):
    """Create: log a new period. The start date defaults to today."""
    if request.method == 'POST':
        form = CycleLogForm(request.POST, user=request.user)
        try:
            with transaction.atomic():
                _lock_member(request.user)
                if form.is_valid():
                    log = form.save(commit=False)
                    log.user = request.user
                    log.save()
                    form.save_m2m()
                    messages.success(request, 'Your period was logged.')
                    return redirect('cycle_list')
        except IntegrityError:
            form.add_error(None, SAVE_CONFLICT_MESSAGE)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CycleLogForm(user=request.user, initial={'start_date': timezone.localdate()})

    return render(request, 'cycles/cycle_form.html', {'form': form, 'is_edit': False})


@require_http_methods(['GET', 'POST'])
@role_required(Profile.Role.MEMBER)
def cycle_update(request, pk):
    """Update: edit one of the member's own logs. Other users' logs return 404."""
    log = get_object_or_404(CycleLog, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CycleLogForm(request.POST, instance=log, user=request.user)
        try:
            with transaction.atomic():
                _lock_member(request.user)
                if form.is_valid():
                    form.save()  # saves the log and its symptoms together
                    messages.success(request, 'Your cycle log was updated.')
                    return redirect('cycle_list')
        except IntegrityError:
            form.add_error(None, SAVE_CONFLICT_MESSAGE)
        messages.error(request, 'Please correct the errors below.')
    else:
        form = CycleLogForm(instance=log, user=request.user)

    return render(
        request, 'cycles/cycle_form.html', {'form': form, 'is_edit': True, 'log': log}
    )


@require_http_methods(['GET', 'POST'])
@role_required(Profile.Role.MEMBER)
def cycle_delete(request, pk):
    """Delete: GET shows a confirmation page, only POST deletes the log."""
    log = get_object_or_404(CycleLog, pk=pk, user=request.user)

    if request.method == 'POST':
        log.delete()
        messages.success(request, 'Your cycle log was deleted.')
        return redirect('cycle_list')

    return render(request, 'cycles/cycle_confirm_delete.html', {'log': log})


@require_GET
@role_required(Profile.Role.ADMIN)
def cycle_admin_list(request):
    """Read-only list of every member's logs, for Admins."""
    query = request.GET.get('q', '').strip()[:MAX_SEARCH_LENGTH]
    logs = CycleLog.objects.select_related('user').prefetch_related('symptoms')
    if query:
        logs = logs.filter(
            Q(user__username__icontains=query)
            | Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
        )
    return render(request, 'cycles/admin_cycle_list.html', {'logs': logs, 'query': query})
