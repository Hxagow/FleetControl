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
    path('<slug:slug>/delete/', views.organization_delete, name='organization_delete'),
    
    # Gestion des membres et invitations
    path('<slug:slug>/invite/', views.invite_user, name='invite_user'),
    path('<slug:slug>/members/', views.organization_members, name='organization_members'),
    path('<slug:slug>/members/<int:member_id>/remove/', views.remove_member, name='remove_member'),
    path('<slug:slug>/members/<int:member_id>/role/', views.change_member_role, name='change_member_role'),
    path('<slug:slug>/invitations/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    path('<slug:slug>/invitations/<int:invitation_id>/cancel/', views.cancel_invitation, name='cancel_invitation'),
    path('<slug:slug>/invitations/<int:invitation_id>/delete/', views.delete_invitation, name='delete_invitation'),
    path('<slug:slug>/leave/', views.leave_organization, name='leave_organization'),
]