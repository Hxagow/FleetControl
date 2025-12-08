from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .models import Organization, Invitation
from .forms import OrganizationForm, InvitationForm
from users.models import OrganizationUser, User
from django.contrib import messages

@login_required
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save()
            OrganizationUser.objects.create(
                user=request.user,
                organization=organization,
                role='admin'
            )
            return redirect('organization_detail', slug=organization.slug)
    else:
        form = OrganizationForm()
    return render(request, 'organizations/organization_form.html', {'form': form})


@login_required
def organization_list(request):
    # Récupérer les organisations dont l'utilisateur est membre
    user_organizations = Organization.objects.filter(organization_users__user=request.user)

    # Récupérer les invitations en attente pour l'utilisateur
    pending_invitations = Invitation.objects.filter(
        email=request.user.email,
        status='pending'
    ).select_related('organization', 'invited_by')
    
    # Filtrer les invitations non expirées
    valid_invitations = [inv for inv in pending_invitations if inv.can_be_accepted()]
    
    return render(request, 'organizations/panel.html', {
        'organizations': user_organizations,
        'pending_invitations': valid_invitations
    })


@login_required
def organization_detail(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est membre de l'organisation
    if not org.organization_users.filter(user=request.user).exists():
        raise PermissionDenied("Vous n'êtes pas membre de cette organisation.")
    
    is_admin = org.organization_users.filter(user=request.user, role='admin').exists()
    return render(request, 'organizations/organization_detail.html', {
        'organization': org,
        'is_admin': is_admin
    })


@login_required
def organization_update(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour modifier l'organisation.")
    
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES, instance=org)
        if form.is_valid():
            form.save()
            return redirect('organization_detail', slug=org.slug)
    else:
        form = OrganizationForm(instance=org)
    return render(request, 'organizations/organization_form.html', {'form': form})


@login_required
def organization_delete(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour supprimer l'organisation.")
    
    if request.method == "POST":
        org.delete()
        return redirect('organizations_panel')
    return redirect('organization_detail', slug=slug)


@login_required
# A CORRIGER
def invite_user(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour inviter des utilisateurs.")
    
    if request.method == "POST":
        form = InvitationForm(request.POST, organization=org)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role'] # Ajout du rôle depuis le formulaire
            
            # Nettoyer les invitations expirées pour cet email dans cette organisation
            expired_invitations = Invitation.objects.filter(email=email, organization=org)
            for inv in expired_invitations:
                if inv.is_expired():
                    inv.delete()
            
            # Vérifier si l'utilisateur existe déjà
            try:
                existing_user = User.objects.get(email=email)
                # Vérifier s'il est déjà membre
                if org.organization_users.filter(user=existing_user).exists():
                    messages.error(request, "Cet utilisateur est déjà membre de l'organisation.")
                    return redirect('organization_detail', slug=slug)
                    
                # Créer l'invitation pour un utilisateur existant
                invitation = Invitation.objects.create(email=email, organization=org, invited_by=request.user, role=role)
                
                # Envoyer email d'information (l'utilisateur verra l'invitation dans ses notifications)
                subject = f"Invitation à rejoindre {org.name}"
                message = render_to_string('organizations/email/invitation_existing_user.html', {'organization': org, 'invitation': invitation, 'invited_by': request.user})
                
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,[email], html_message=message)
                
                messages.success(request, f"Invitation envoyée à {email}")
                
            except User.DoesNotExist:
                # Créer l'invitation pour un nouvel utilisateur
                invitation = Invitation.objects.create(email=email, organization=org, invited_by=request.user, role=role)
                
                # Envoyer email avec lien d'inscription
                signup_url = request.build_absolute_uri(
                    reverse('account_signup') + f'?invitation={invitation.token}'
                )
                
                subject = f"Invitation à rejoindre {org.name}"
                message = render_to_string('organizations/email/invitation_new_user.html', {
                    'organization': org,
                    'invitation': invitation,
                    'signup_url': signup_url,
                    'invited_by': request.user
                })
                
                send_mail(subject,message, settings.DEFAULT_FROM_EMAIL, [email], html_message=message)
                
                messages.success(request, f"Invitation envoyée à {email} en tant que {role}")
            
            return redirect('organization_detail', slug=slug)
    else:
        form = InvitationForm(organization=org)
    
    return render(request, 'organizations/invite_user.html', {
        'form': form,
        'organization': org
    })


@login_required
def organization_members(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour gérer les membres.")
    
    # Récupérer les membres et invitations
    members = org.organization_users.all().select_related('user').order_by('role', 'user__first_name', 'user__email')
    invitations = org.invitations.all().select_related('invited_by').order_by('-created_at')
    
    return render(request, 'organizations/members_management.html', {
        'organization': org,
        'members': members,
        'invitations': invitations
    })


@login_required
def remove_member(request, slug, member_id):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour supprimer des membres.")
    
    member = get_object_or_404(OrganizationUser, id=member_id, organization=org)

    # Empêcher la suppression du dernier admin
    admin_count = org.organization_users.filter(role='admin').count()
    if member.role == 'admin' and admin_count <= 1:
        messages.error(request, "Impossible de supprimer le dernier administrateur de l'organisation.")
        return redirect('organization_members', slug=slug)
    
    # Empêcher l'auto-suppression si c'est le dernier admin
    if member.user == request.user and member.role == 'admin' and admin_count <= 1:
        messages.error(request, "Vous ne pouvez pas quitter l'organisation car vous êtes le seul administrateur.")
        return redirect('organization_members', slug=slug)
    
    user_name = member.user.first_name or member.user.email
    user_email = member.user.email
    
    # Supprimer le membership
    member.delete()
    
    # Supprimer aussi toutes les invitations en attente pour cet email dans cette organisation
    Invitation.objects.filter(email=user_email, organization=org).delete()
    
    messages.success(request, f"{user_name} a été retiré de l'organisation.")
    return redirect('organization_members', slug=slug)


@login_required
def change_member_role(request, slug, member_id):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour modifier les rôles.")
    
    member = get_object_or_404(OrganizationUser, id=member_id, organization=org)
    new_role = request.POST.get('role')
    
    if new_role not in ['admin', 'member']:
        messages.error(request, "Rôle invalide.")
        return redirect('organization_members', slug=slug)
    
    # Empêcher qu'un admin se rétrograde lui-même
    if member.user == request.user and member.role == 'admin' and new_role == 'member':
        messages.error(request, "Vous ne pouvez pas vous rétrograder vous-même.")
        return redirect('organization_members', slug=slug)
    
    # Empêcher la rétrogradation du dernier admin
    admin_count = org.organization_users.filter(role='admin').count()
    if member.role == 'admin' and new_role == 'member' and admin_count <= 1:
        messages.error(request, "Impossible de rétrograder le dernier administrateur.")
        return redirect('organization_members', slug=slug)
    
    member.role = new_role
    member.save()
    
    user_name = member.user.first_name or member.user.email
    role_name = "administrateur" if new_role == 'admin' else "membre"
    messages.success(request, f"{user_name} est maintenant {role_name}.")
    return redirect('organization_members', slug=slug)


@login_required
def cancel_invitation(request, slug, invitation_id):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour annuler des invitations.")
    
    invitation = get_object_or_404(Invitation, id=invitation_id, organization=org)
    
    if invitation.status != 'pending':
        messages.error(request, "Cette invitation ne peut plus être annulée.")
        return redirect('organization_members', slug=slug)
    
    invitation.delete()
    messages.success(request, f"Invitation pour {invitation.email} annulée.")
    return redirect('organization_members', slug=slug)

# Supprimer une invitation des "Invitations en attente"
@login_required()
def delete_invitation(request, slug, invitation_id):
    org = get_object_or_404(Organization, slug=slug)
    # Permettre la suppression uniquement aux administrateurs
    if not org.organization_users.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour supprimer des invitations.")

    invitation = get_object_or_404(Invitation, id=invitation_id, organization=org)

    email = invitation.email
    status_label = invitation.get_status_display()

    invitation.delete()
    messages.success(
        request,
        f"Invitation ({status_label}) pour {email} supprimée de l'historique."
    )
    return redirect('organization_members', slug=slug)


@login_required
def leave_organization(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    
    # Vérifier si l'utilisateur est membre de l'organisation
    try:
        membership = org.organization_users.get(user=request.user)
    except OrganizationUser.DoesNotExist:
        messages.error(request, "Vous n'êtes pas membre de cette organisation.")
        return redirect('organizations_panel')
    
    # Empêcher le dernier admin de quitter
    admin_count = org.organization_users.filter(role='admin').count()
    if membership.role == 'admin' and admin_count <= 1:
        messages.error(request, "Vous ne pouvez pas quitter l'organisation car vous êtes le seul administrateur. Promouvez d'abord un autre membre.")
        return redirect('organization_detail', slug=slug)
    
    # Quitter l'organisation
    org_name = org.name
    user_email = request.user.email
    
    # Supprimer le lien utilisateur ↔ organisation
    membership.delete()
    
    # Supprimer aussi toutes les invitations en attente pour cet email dans cette organisation
    Invitation.objects.filter(email=user_email, organization=org).delete()
    
    messages.success(request, f"Vous avez quitté l'organisation {org_name}.")
    return redirect('organizations_panel')