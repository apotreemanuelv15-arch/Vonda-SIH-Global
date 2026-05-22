from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls), # Syntaxe simplifiée et standard
    path('pharmacy/', include('pharmacy.urls')),
]