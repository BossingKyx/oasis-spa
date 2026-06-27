"""URL routes for the spa app."""
from django.urls import path

from . import views

urlpatterns = [
    # Public customer self-booking (no login)
    path('__diag/', views._diag),
    path('book/', views.public_book, name='public_book'),
    path('book/done/<int:pk>/', views.public_book_done, name='public_book_done'),

    path('', views.dashboard, name='dashboard'),

    # Kanban board
    path('board/', views.board, name='board'),
    path('booking/<int:pk>/status/', views.booking_set_status, name='booking_set_status'),

    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/new/', views.booking_create, name='booking_create'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:pk>/receipt/', views.receipt, name='receipt'),

    # Payments
    path('bookings/<int:pk>/pay/', views.payment_create, name='payment_create'),

    # Customers (CRM)
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/quick-add/', views.customer_quick_create, name='customer_quick_create'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),

    # Expenses / petty cash
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/new/', views.expense_create, name='expense_create'),
    path('expenses/scan-receipt/', views.expense_scan_receipt, name='expense_scan_receipt'),

    # Reports
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/daily/excel/', views.daily_report_excel, name='daily_report_excel'),
    path('reports/daily/pdf/', views.daily_report_pdf, name='daily_report_pdf'),
]
