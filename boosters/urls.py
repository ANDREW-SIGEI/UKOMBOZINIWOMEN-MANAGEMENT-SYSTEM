from django.urls import path
from django.views.generic import TemplateView

app_name = 'boosters'

urlpatterns = [
    # Temporary placeholder URL pattern
    path('', TemplateView.as_view(template_name='base.html'), name='index'),
] 