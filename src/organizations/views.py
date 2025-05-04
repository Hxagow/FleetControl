from django.shortcuts import render, redirect, get_object_or_404
from .models import Organization
from .forms import OrganizationForm
from django.contrib.auth.decorators import login_required

@login_required
def organization_create(request):
    if request.method == "POST":
        form = OrganizationForm(request.POST, request.FILES)
        if form.is_valid():
            organization = form.save()
            return redirect('organization_detail', slug=organization.slug)
    else:
        form = OrganizationForm()
    return render(request, 'organizations/organization_form.html', {'form': form})


@login_required
def organization_list(request):
    orgs = Organization.objects.all()
    return render(request, 'organizations/panel.html', {'organizations': orgs})


@login_required
def organization_detail(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    return render(request, 'organizations/organization_detail.html', {'organization': org})


@login_required
def organization_update(request, slug):
    org = get_object_or_404(Organization, slug=slug)
    form = OrganizationForm(request.POST or None, request.FILES or None, instance=org)
    if form.is_valid():
        form.save()
        return redirect('organization_detail', slug=org.slug)
    return render(request, 'organizations/organization_form.html', {'form': form})