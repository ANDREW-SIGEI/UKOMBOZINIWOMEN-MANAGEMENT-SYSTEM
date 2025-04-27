"""
URL configuration for ukomboziniwomen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from dashboard.views import offline_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    
    # App URLs
    path('user-management/', include('user_management.urls', namespace='user_management')),
    path('tablebanking/', include('tablebanking.urls', namespace='tablebanking')),
    path('boosters/', include('boosters.urls', namespace='boosters')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('ukombozini-products/', include('ukombozini_products.urls', namespace='ukombozini_products')),
    
    # Offline page
    path('offline/', offline_view, name='offline'),
    
    # Test page to check browser access
    path('test/', TemplateView.as_view(template_name='test.html'), name='test'),
    
    # Default redirect to dashboard - Changed to direct template for testing
    path('', TemplateView.as_view(template_name='test.html'), name='home'),
]

# Add static and media files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
