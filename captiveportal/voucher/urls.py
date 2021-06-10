from django.urls import path
from . import views

app_name = 'voucher'

urlpatterns = [
    path('', views.PortalListView.as_view(), name='index'),
    path('portals/<int:portal_id>/', views.printselection, name='portal'),
    path('print/<int:portal_id>/<int:roll_id>/<str:printer_type>/', views.print, name='print'),
]