from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Organization
from .forms import OrganizationForm
from users.models import Membership, User
from django.contrib import messages

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