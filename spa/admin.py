from django.contrib import admin

from .models import (Branch, Service, Customer, StaffProfile, Booking,
                     Payment, Expense)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'is_active')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'mobile', 'facebook_name', 'visit_count')
    search_fields = ('full_name', 'mobile', 'facebook_name')


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'role', 'branch', 'base_pay', 'commission_rate')
    list_filter = ('role', 'branch')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'branch', 'service_type', 'status',
                    'therapist', 'scheduled_for')
    list_filter = ('status', 'branch', 'service_type')
    search_fields = ('customer__full_name',)
    inlines = [PaymentInline]
    filter_horizontal = ('services',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'method', 'amount', 'paid_at')
    list_filter = ('method',)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('spent_on', 'branch', 'category', 'amount')
    list_filter = ('branch', 'category')
