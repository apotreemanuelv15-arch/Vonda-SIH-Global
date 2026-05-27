from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='inventaire/', permanent=True)), 
    path('accounts/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('', include('pharmacy.urls')), 
]