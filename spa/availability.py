"""Time-slot availability for customer self-booking.

A branch is open OPEN_TIME-CLOSE_TIME daily; slots are SLOT_MINUTES long.
A slot's capacity is the number of active therapists at that branch, so a
slot shows as full once that many bookings already sit in it.
"""
from datetime import datetime, time, timedelta

from django.conf import settings
from django.utils import timezone

from .models import Booking, StaffProfile


def _minutes(hhmm, default):
    try:
        h, m = str(hhmm).split(':')
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return default


def slot_capacity(branch):
    """How many bookings can run at the same time = active therapists (min 1)."""
    n = StaffProfile.objects.filter(
        role=StaffProfile.THERAPIST, branch=branch, user__is_active=True).count()
    return max(n, 1)


def build_slots(branch, day):
    """Return a list of {start, label, available, full} for the day.

    Past slots (for today) are omitted.
    """
    cfg = settings.OASIS
    length = int(cfg.get('SLOT_MINUTES', 60))
    open_min = _minutes(cfg.get('OPEN_TIME'), 14 * 60)
    close_min = _minutes(cfg.get('CLOSE_TIME'), 0)
    if close_min <= open_min:           # closes after midnight (e.g. 00:00)
        close_min += 24 * 60

    tz = timezone.get_current_timezone()
    midnight = datetime.combine(day, time(0, 0))
    open_dt = timezone.make_aware(midnight + timedelta(minutes=open_min), tz)
    close_dt = timezone.make_aware(midnight + timedelta(minutes=close_min), tz)
    delta = timedelta(minutes=length)
    capacity = slot_capacity(branch)
    now = timezone.now()

    slots = []
    start = open_dt
    while start + delta <= close_dt:
        end = start + delta
        if start > now:                 # skip past/started slots
            taken = (Booking.objects
                     .filter(branch=branch, scheduled_for__gte=start, scheduled_for__lt=end)
                     .exclude(status__in=[Booking.CANCELLED, Booking.NO_SHOW])
                     .count())
            slots.append({
                'start': start,
                'label': timezone.localtime(start).strftime('%I:%M %p').lstrip('0'),
                'available': taken < capacity,
                'full': taken >= capacity,
            })
        start = end
    return slots


def is_slot_open(branch, start_dt):
    """Re-check at submit time that a specific slot still has room."""
    length = int(settings.OASIS.get('SLOT_MINUTES', 60))
    end = start_dt + timedelta(minutes=length)
    taken = (Booking.objects
             .filter(branch=branch, scheduled_for__gte=start_dt, scheduled_for__lt=end)
             .exclude(status__in=[Booking.CANCELLED, Booking.NO_SHOW])
             .count())
    return taken < slot_capacity(branch)
