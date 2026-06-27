"""Weekly payroll computation (Sunday–Saturday).

Pay = regular hours × hourly rate
    + overtime hours (>STANDARD_DAY_HOURS/day) × hourly rate × OT_MULTIPLIER
    + commission (% of the price of services the staff performed that week).
"""
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.utils import timezone

from .models import Booking, PayrollMark, StaffProfile, TimeLog

TWOPLACES = Decimal('0.01')


def _q(value):
    return Decimal(value).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def week_bounds(any_date):
    """Return (sunday_start, saturday_end) for the week containing any_date."""
    # Python weekday(): Mon=0 … Sun=6. Days since the most recent Sunday:
    offset = (any_date.weekday() + 1) % 7
    start = any_date - timedelta(days=offset)
    return start, start + timedelta(days=6)


def _cfg():
    std = Decimal(str(settings.OASIS.get('STANDARD_DAY_HOURS', 10)))
    otm = Decimal(str(settings.OASIS.get('OT_MULTIPLIER', 1.25)))
    return std, otm


def compute_payslip(staff, week_start):
    """Compute one staff member's payslip dict for the week starting week_start."""
    std, otm = _cfg()
    week_end = week_start + timedelta(days=6)
    rate = staff.hourly_rate or Decimal('0')
    crate = (staff.commission_rate or Decimal('0')) / Decimal('100')

    # --- Hours from completed shifts, grouped per day (OT is per-day over std) ---
    logs = TimeLog.objects.filter(
        staff=staff, clock_out__isnull=False,
        clock_in__date__gte=week_start, clock_in__date__lte=week_end)
    per_day = {}
    for lg in logs:
        d = timezone.localtime(lg.clock_in).date()
        per_day[d] = per_day.get(d, Decimal('0')) + lg.hours

    reg_hours = Decimal('0')
    ot_hours = Decimal('0')
    for hours in per_day.values():
        if hours > std:
            reg_hours += std
            ot_hours += (hours - std)
        else:
            reg_hours += hours

    base = reg_hours * rate
    ot_pay = ot_hours * rate * otm

    # --- Commission from services performed this week ---
    bookings = Booking.objects.filter(
        therapist=staff,
        status__in=[Booking.COMPLETED, Booking.PAID, Booking.CLOSED],
    ).prefetch_related('services')
    service_total = Decimal('0')
    completed = 0
    for b in bookings:
        when = (timezone.localtime(b.finished_at).date()
                if b.finished_at else b.scheduled_for.date())
        if week_start <= when <= week_end:
            service_total += Decimal(str(b.service_total))
            completed += 1
    commission = service_total * crate
    total = base + ot_pay + commission

    paid = PayrollMark.objects.filter(staff=staff, week_start=week_start).first()
    return {
        'staff': staff,
        'week_start': week_start,
        'week_end': week_end,
        'reg_hours': reg_hours.quantize(TWOPLACES),
        'ot_hours': ot_hours.quantize(TWOPLACES),
        'hourly_rate': rate,
        'base': _q(base),
        'ot_pay': _q(ot_pay),
        'base_total': _q(base + ot_pay),
        'commission_rate': staff.commission_rate or Decimal('0'),
        'service_total': _q(service_total),
        'services_count': completed,
        'commission': _q(commission),
        'total': _q(total),
        'is_paid': bool(paid),
        'paid_at': paid.paid_at if paid else None,
    }


def compute_payroll(week_start, staff_qs=None):
    """Payslips for all (or given) staff, plus grand totals."""
    if staff_qs is None:
        staff_qs = StaffProfile.objects.select_related('user').all()
    slips = [compute_payslip(s, week_start) for s in staff_qs]
    totals = {
        'base': _q(sum((s['base'] for s in slips), Decimal('0'))),
        'ot_pay': _q(sum((s['ot_pay'] for s in slips), Decimal('0'))),
        'base_total': _q(sum((s['base_total'] for s in slips), Decimal('0'))),
        'commission': _q(sum((s['commission'] for s in slips), Decimal('0'))),
        'total': _q(sum((s['total'] for s in slips), Decimal('0'))),
    }
    return slips, totals
