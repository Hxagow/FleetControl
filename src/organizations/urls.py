from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.organization_list, name='organizations_panel'),
    
    path('create/', views.organization_create, name='organization_create'),
    path('<slug:slug>/', views.organization_detail, name='organization_detail'),
    path('<slug:slug>/update/', views.organization_update, name='organization_update'),
]