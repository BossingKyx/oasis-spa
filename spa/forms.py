"""Forms for Oasis on the Go Spa."""
from django import forms
from django.conf import settings

from .models import Booking, Customer, Payment, Expense, Service, StaffProfile


def _cfg(key, default=None):
    return settings.OASIS.get(key, default)


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'mobile', 'facebook_name', 'address', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }


class BookingForm(forms.ModelForm):
    """Manual booking entry — covers Facebook / phone / walk-in intake."""
    services = forms.ModelMultipleChoiceField(
        queryset=Service.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Booking
        fields = ['customer', 'branch', 'services', 'therapist', 'service_type',
                  'channel', 'scheduled_for', 'home_address', 'travel_notes', 'notes']
        widgets = {
            'scheduled_for': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'travel_notes': forms.TextInput(),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_for'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['therapist'].queryset = StaffProfile.objects.filter(
            role=StaffProfile.THERAPIST)
        self.fields['therapist'].required = False
        channels = _cfg('BOOKING_CHANNELS', [])
        self.fields['channel'] = forms.ChoiceField(
            choices=[(c, c) for c in channels], required=True)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('service_type') == Booking.HOME and not cleaned.get('home_address'):
            self.add_error('home_address', 'Home address is required for home service.')
        return cleaned


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method', 'amount', 'reference', 'screenshot', 'paid_at']
        widgets = {
            'paid_at': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['paid_at'].input_formats = ['%Y-%m-%dT%H:%M']
        methods = _cfg('PAYMENT_METHODS', [])
        self.fields['method'] = forms.ChoiceField(choices=[(m, m) for m in methods])


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['branch', 'category', 'description', 'supplier_name', 'supplier_tin',
                  'supplier_address', 'reference', 'amount', 'receipt', 'spent_on']
        widgets = {
            'spent_on': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['spent_on'].input_formats = ['%Y-%m-%d']
        cats = _cfg('EXPENSE_CATEGORIES', [])
        self.fields['category'] = forms.ChoiceField(choices=[(c, c) for c in cats])
