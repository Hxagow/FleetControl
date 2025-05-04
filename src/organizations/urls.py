from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('', TemplateView.as_view(template_name="organization/panel.html"), name='organizations_panel'),
]