"""URL routes for the spa app."""
from django.urls import path

from . import views

urlpatterns = [
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

    # Reports
    path('reports/daily/', views.daily_report, name='daily_report'),
    path('reports/daily/excel/', views.daily_report_excel, name='daily_report_excel'),
    path('reports/daily/pdf/', views.daily_report_pdf, name='daily_report_pdf'),
]
