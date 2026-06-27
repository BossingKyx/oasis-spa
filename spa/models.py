"""Data model for Oasis on the Go Spa — Phase 1 (MVP)."""
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Branch(models.Model):
    """A physical spa branch (Gen Trias / Trece Martires)."""
    name = models.CharField(max_length=80, unique=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'branches'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    """A service the spa offers (massage, nails, waxing, head spa, etc.)."""
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, blank=True)
    duration_minutes = models.PositiveIntegerField(default=60)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f'{self.name} (₱{self.price:,.0f})'


class Customer(models.Model):
    """A spa client and their contact + preference history."""
    full_name = models.CharField(max_length=160)
    mobile = models.CharField(max_length=40, blank=True)
    facebook_name = models.CharField('Facebook name / handle', max_length=160, blank=True)
    address = models.CharField(max_length=255, blank=True)
    notes = models.TextField('Notes / preferences', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def visit_count(self):
        return self.bookings.filter(
            status__in=[Booking.COMPLETED, Booking.PAID, Booking.CLOSED]
        ).count()

    @property
    def total_spend(self):
        agg = Payment.objects.filter(booking__customer=self).aggregate(t=models.Sum('amount'))
        return agg['t'] or 0


class StaffProfile(models.Model):
    """Extends the auth User with a spa role and home branch.

    Roles:
      OWNER     — full access across both branches (Owner / Admin)
      THERAPIST — limited: own assigned bookings, the board, time logging
    """
    OWNER = 'OWNER'
    THERAPIST = 'THERAPIST'
    ROLE_CHOICES = [
        (OWNER, 'Owner / Admin'),
        (THERAPIST, 'Therapist / Staff'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=THERAPIST)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='staff')
    mobile = models.CharField(max_length=40, blank=True)
    # Base + commission scaffolding — fully used in Phase 2 payroll.
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission_rate = models.DecimalField('Commission rate (%)', max_digits=5,
                                          decimal_places=2, default=0)

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} ({self.get_role_display()})'

    @property
    def is_owner(self):
        return self.role == self.OWNER

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.username


class Booking(models.Model):
    """One service session: the heart of the workflow."""
    # Service location type
    WALK_IN = 'WALKIN'
    HOME = 'HOME'
    TYPE_CHOICES = [
        (WALK_IN, 'Walk-in'),
        (HOME, 'Home service'),
    ]

    # Status flow (drives the Kanban board)
    REQUESTED = 'REQUESTED'
    CONFIRMED = 'CONFIRMED'
    ARRIVED = 'ARRIVED'
    IN_SERVICE = 'IN_SERVICE'
    COMPLETED = 'COMPLETED'
    PAID = 'PAID'
    CLOSED = 'CLOSED'
    NO_SHOW = 'NO_SHOW'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (REQUESTED, 'Requested'),
        (CONFIRMED, 'Confirmed'),
        (ARRIVED, 'Arrived / En route'),
        (IN_SERVICE, 'In Service'),
        (COMPLETED, 'Completed'),
        (PAID, 'Paid'),
        (CLOSED, 'Closed'),
        (NO_SHOW, 'No-show'),
        (CANCELLED, 'Cancelled'),
    ]
    # Columns shown on the Kanban board, in order.
    BOARD_STATUSES = [REQUESTED, CONFIRMED, ARRIVED, IN_SERVICE, COMPLETED, PAID, CLOSED]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='bookings')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='bookings')
    services = models.ManyToManyField(Service, related_name='bookings')
    therapist = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='bookings',
                                  limit_choices_to={'role': StaffProfile.THERAPIST})

    service_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=WALK_IN)
    channel = models.CharField(max_length=40, default='Walk-in',
                               help_text='Where the booking came from (Facebook / Phone / Walk-in)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=REQUESTED)

    scheduled_for = models.DateTimeField(default=timezone.now)
    # Home-service details
    home_address = models.CharField(max_length=255, blank=True)
    travel_notes = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    # Service start/stop stamps (server time) — replaces the Messenger "IN 60mins…" logs.
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Channel-agnostic intake hook for future Facebook/ManyChat automation.
    external_source = models.CharField(max_length=40, blank=True)
    external_ref = models.CharField(max_length=120, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='bookings_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_for']

    def __str__(self):
        return f'#{self.pk} {self.customer} — {self.branch}'

    @property
    def service_total(self):
        return sum((s.price for s in self.services.all()), 0)

    @property
    def amount_paid(self):
        agg = self.payments.aggregate(t=models.Sum('amount'))
        return agg['t'] or 0

    @property
    def balance(self):
        return self.service_total - self.amount_paid

    @property
    def is_paid(self):
        return self.service_total > 0 and self.amount_paid >= self.service_total

    @property
    def services_label(self):
        return ', '.join(s.name for s in self.services.all())

    @property
    def duration_label(self):
        if self.started_at and self.finished_at:
            mins = int((self.finished_at - self.started_at).total_seconds() // 60)
            return f'{mins} min'
        return ''


class Payment(models.Model):
    """A payment recorded against a booking."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    screenshot = models.ImageField(upload_to='payments/%Y/%m/', blank=True, null=True,
                                   help_text='GCash / QRPH / card proof')
    reference = models.CharField(max_length=120, blank=True)
    paid_at = models.DateTimeField(default=timezone.now)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-paid_at']

    def __str__(self):
        return f'₱{self.amount:,.2f} {self.method} — {self.booking}'


class Expense(models.Model):
    """A business expense / petty-cash outflow."""
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='expenses')
    category = models.CharField(max_length=60)
    description = models.CharField(max_length=255, blank=True)
    supplier_name = models.CharField('Supplier / vendor', max_length=160, blank=True)
    supplier_tin = models.CharField('Supplier TIN', max_length=40, blank=True)
    supplier_address = models.CharField('Supplier address', max_length=255, blank=True)
    reference = models.CharField('Receipt / invoice no.', max_length=120, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt = models.ImageField(upload_to='expenses/%Y/%m/', blank=True, null=True)
    spent_on = models.DateField(default=timezone.localdate)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-spent_on', '-created_at']

    def __str__(self):
        return f'₱{self.amount:,.2f} {self.category} — {self.branch}'
