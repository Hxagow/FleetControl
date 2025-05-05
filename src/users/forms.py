from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
from organizations.models import Organization
from .models import Membership

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label=_('Prénom'),
        widget=forms.TextInput(attrs={'placeholder': _('Votre prénom')})
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Nom'),
        widget=forms.TextInput(attrs={'placeholder': _('Votre nom')})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'request'):
            # Récupérer l'email depuis les paramètres GET
            email = self.request.GET.get('email')
            if email:
                self.fields['email'].initial = email
                self.fields['email'].widget.attrs['readonly'] = True

    def save(self, request):
        user = super().save(request)
        
        # Vérifier si l'inscription vient d'une invitation
        org_slug = request.GET.get('organization')
        role = request.GET.get('role')
        
        if org_slug and role:
            try:
                organization = Organization.objects.get(slug=org_slug)
                # Créer l'adhésion avec le rôle spécifié
                Membership.objects.create(
                    user=user,
                    organization=organization,
                    role=role
                )
            except Organization.DoesNotExist:
                pass
        
        return user 