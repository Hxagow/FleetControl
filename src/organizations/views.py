from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Organization
from .forms import OrganizationForm, InvitationForm
from users.models import Membership, User
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags
from urllib.parse import urlencode

@login_required
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save()
            Membership.objects.create(
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
    user_organizations = Organization.objects.filter(memberships__user=request.user)
    return render(request, 'organizations/panel.html', {'organizations': user_organizations})


@login_required
def organization_detail(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est membre de l'organisation
    if not org.memberships.filter(user=request.user).exists():
        raise PermissionDenied("Vous n'êtes pas membre de cette organisation.")
    
    is_admin = org.memberships.filter(user=request.user, role='admin').exists()
    return render(request, 'organizations/organization_detail.html', {
        'organization': org,
        'is_admin': is_admin
    })


@login_required
def organization_update(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.memberships.filter(user=request.user, role='admin').exists():
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
    if not org.memberships.filter(user=request.user, role='admin').exists():
        raise PermissionDenied("Vous devez être administrateur pour supprimer l'organisation.")
    
    if request.method == "POST":
        org.delete()
        return redirect('organizations_panel')
    return redirect('organization_detail', slug=slug)


@login_required
def organization_invite(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    
    # Vérifier si l'utilisateur est admin de l'organisation
    if not org.memberships.filter(user=request.user, role='admin').exists():
        messages.error(request, "Vous n'avez pas les droits pour inviter des membres.")
        return redirect('organization_detail', slug=slug)
    
    if request.method == "POST":
        form = InvitationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            
            # Vérifier si l'utilisateur existe déjà
            user = User.objects.filter(email=email).first()
            
            # Générer l'URL d'invitation
            current_site = get_current_site(request)
            if user:
                # L'utilisateur existe déjà
                if org.memberships.filter(user=user).exists():
                    messages.error(request, "Cet utilisateur est déjà membre de l'organisation.")
                    return redirect('organization_invite', slug=slug)
                
                # Envoyer un email d'invitation à rejoindre l'organisation
                context = {
                    'organization': org,
                    'inviter': request.user,
                    'domain': current_site.domain,
                    'join_url': request.build_absolute_uri(
                        reverse('join_organization', kwargs={'slug': org.slug})
                    )
                }
                
                html_message = render_to_string('organizations/email/existing_user_invitation.html', context)
                try:
                    send_mail(
                        subject=f'Invitation à rejoindre {org.name}',
                        message=strip_tags(html_message),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message
                    )
                    messages.success(request, f"Une invitation a été envoyée à {email}.")
                except Exception as e:
                    messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email. Veuillez réessayer plus tard.")
                    return redirect('organization_invite', slug=slug)
            else:
                # L'utilisateur n'existe pas encore
                context = {
                    'organization': org,
                    'inviter': request.user,
                    'domain': current_site.domain,
                    'signup_url': request.build_absolute_uri(
                        reverse('account_signup') + '?' + urlencode({
                            'organization': org.slug,
                            'email': email,
                            'role': role
                        })
                    )
                }
                
                html_message = render_to_string('organizations/email/new_user_invitation.html', context)
                try:
                    send_mail(
                        subject=f'Invitation à rejoindre {org.name}',
                        message=strip_tags(html_message),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email],
                        html_message=html_message
                    )
                    messages.success(request, f"Une invitation a été envoyée à {email}.")
                except Exception as e:
                    messages.error(request, "Une erreur s'est produite lors de l'envoi de l'email. Veuillez réessayer plus tard.")
                    return redirect('organization_invite', slug=slug)
            
            return redirect('organization_detail', slug=slug)
    else:
        form = InvitationForm()
    
    return render(request, 'organizations/invite_member.html', {
        'form': form,
        'organization': org
    })


def join_organization(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    
    # Si l'utilisateur n'est pas connecté, rediriger vers la page de connexion
    if not request.user.is_authenticated:
        # Construire l'URL de redirection après la connexion
        next_url = reverse('join_organization', kwargs={'slug': slug})
        if request.GET.get('role'):
            next_url += f"?role={request.GET.get('role')}"
        
        # Rediriger vers la page de connexion avec le paramètre next
        login_url = reverse('account_login')
        redirect_url = f"{login_url}?{urlencode({'next': next_url})}"
        return redirect(redirect_url)
    
    # Vérifier si l'utilisateur n'est pas déjà membre
    if org.memberships.filter(user=request.user).exists():
        messages.warning(request, "Vous êtes déjà membre de cette organisation.")
        return redirect('organization_detail', slug=slug)
    
    if request.method == "POST":
        # Créer l'adhésion avec le rôle spécifié dans l'URL
        role = request.GET.get('role', 'member')  # Par défaut, le rôle est 'member'
        Membership.objects.create(
            user=request.user,
            organization=org,
            role=role
        )
        messages.success(request, f"Vous avez rejoint l'organisation {org.name}.")
        return redirect('organization_detail', slug=slug)
    
    return render(request, 'organizations/join_confirmation.html', {
        'organization': org
    })