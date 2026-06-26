"""Seed branches, services, demo accounts, and a little sample data.

Run:  python manage.py seed_demo
Safe to re-run — it uses get_or_create. Wipe the DB before go-live.
"""
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from spa.models import (Branch, Service, Customer, StaffProfile, Booking,
                        Payment, Expense)


class Command(BaseCommand):
    help = 'Seed demo data for Oasis on the Go Spa.'

    def handle(self, *args, **opts):
        # Branches
        gentrias, _ = Branch.objects.get_or_create(
            name='General Trias',
            defaults={'address': 'General Trias, Cavite', 'phone': '0917-000-0001'})
        trece, _ = Branch.objects.get_or_create(
            name='Trece Martires',
            defaults={'address': 'Trece Martires, Cavite', 'phone': '0917-000-0002'})

        # Services
        services = [
            ('Swedish Massage', 'Massage', 60, 450),
            ('Deep Tissue Massage', 'Massage', 60, 550),
            ('Foot Massage', 'Massage', 45, 300),
            ('Manicure', 'Nails', 45, 200),
            ('Pedicure', 'Nails', 45, 250),
            ('Gel Polish', 'Nails', 60, 400),
            ('Underarm Wax', 'Waxing', 20, 250),
            ('Leg Wax', 'Waxing', 40, 500),
            ('Head Spa', 'Head Spa', 60, 600),
        ]
        svc_objs = {}
        for name, cat, dur, price in services:
            s, _ = Service.objects.get_or_create(
                name=name,
                defaults={'category': cat, 'duration_minutes': dur, 'price': Decimal(price)})
            svc_objs[name] = s

        # Owner account
        owner, created = User.objects.get_or_create(
            username='owner',
            defaults={'first_name': 'Spa', 'last_name': 'Owner',
                      'is_staff': True, 'is_superuser': True})
        if created:
            owner.set_password('oasis123')
            owner.save()
        StaffProfile.objects.get_or_create(
            user=owner, defaults={'role': StaffProfile.OWNER, 'branch': gentrias})

        # Therapists
        therapists = []
        for i, (uname, fname, branch) in enumerate([
                ('therapist1', 'Maria', gentrias),
                ('therapist2', 'Joy', trece)], start=1):
            u, c = User.objects.get_or_create(
                username=uname, defaults={'first_name': fname, 'last_name': 'Therapist'})
            if c:
                u.set_password('oasis123')
                u.save()
            p, _ = StaffProfile.objects.get_or_create(
                user=u, defaults={'role': StaffProfile.THERAPIST, 'branch': branch,
                                  'base_pay': Decimal('400'), 'commission_rate': Decimal('10')})
            therapists.append(p)

        # Sample customers
        custs = []
        for name, mob, fb in [
                ('Ana Reyes', '0917-111-1111', 'Ana Reyes'),
                ('Liza Cruz', '0917-222-2222', 'Liza C'),
                ('Mark Santos', '0917-333-3333', 'Mark S')]:
            c, _ = Customer.objects.get_or_create(
                full_name=name, defaults={'mobile': mob, 'facebook_name': fb})
            custs.append(c)

        # A few sample bookings today (only if none exist yet)
        if not Booking.objects.exists():
            now = timezone.now()
            samples = [
                (custs[0], gentrias, ['Swedish Massage'], therapists[0],
                 Booking.WALK_IN, 'Walk-in', Booking.IN_SERVICE),
                (custs[1], gentrias, ['Manicure', 'Pedicure'], therapists[0],
                 Booking.WALK_IN, 'Facebook', Booking.CONFIRMED),
                (custs[2], trece, ['Head Spa'], therapists[1],
                 Booking.HOME, 'Phone', Booking.PAID),
            ]
            for cust, br, svcs, ther, typ, ch, status in samples:
                b = Booking.objects.create(
                    customer=cust, branch=br, therapist=ther, service_type=typ,
                    channel=ch, status=status, scheduled_for=now,
                    home_address='123 Sample St, Cavite' if typ == Booking.HOME else '',
                    created_by=owner)
                for sn in svcs:
                    b.services.add(svc_objs[sn])
                if status in (Booking.IN_SERVICE, Booking.PAID):
                    b.started_at = now - timedelta(minutes=40)
                if status == Booking.PAID:
                    b.finished_at = now - timedelta(minutes=5)
                    b.save()
                    Payment.objects.create(
                        booking=b, method='GCash', amount=b.service_total,
                        paid_at=now, recorded_by=owner)
                else:
                    b.save()

            # A sample expense
            Expense.objects.create(
                branch=gentrias, category='Supplies', description='Massage oil restock',
                amount=Decimal('850'), recorded_by=owner)

        self.stdout.write(self.style.SUCCESS(
            'Seed complete. Login: owner/oasis123 (Owner), therapist1/oasis123 (Therapist).'))
