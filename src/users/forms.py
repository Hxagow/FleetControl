from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from organizations.models import Organization
from .models import OrganizationUser

User = get_user_model()


class ProfileForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': _('Prénom'),
            'last_name': _('Nom'),
            'email': _('Email'),
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Votre prénom')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input', 
                'placeholder': _('Votre nom')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input',
                'placeholder': _('Votre email')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = True

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=30,
        label=_('Prénom'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre prénom'),
            'class': 'input'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        label=_('Nom'),
        widget=forms.TextInput(attrs={
            'placeholder': _('Votre nom'),
            'class': 'input'
        })
    )

    def __init__(self, *args, **kwargs):
        # Récupérer la request depuis kwargs si elle existe
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if request:
            # Récupérer le token d'invitation depuis les paramètres GET
            invitation_token = request.GET.get('invitation')
            if invitation_token:
                from organizations.models import Invitation
                try:
                    invitation = Invitation.objects.get(token=invitation_token)
                    if invitation.can_be_accepted():
                        self.fields['email'].initial = invitation.email
                        self.fields['email'].widget.attrs['readonly'] = True
                        # Stocker le token pour l'utiliser dans save()
                        self._invitation_token = invitation_token
                        # Stocker dans la session pour les signaux
                        request.session['invitation_token'] = str(invitation_token)
                except Invitation.DoesNotExist:
                    pass
            else:
                # Récupérer l'email depuis les paramètres GET (compatibilité)
                email = request.GET.get('email')
                if email:
                    self.fields['email'].initial = email
                    self.fields['email'].widget.attrs['readonly'] = True
        
        # Appliquer les classes CSS à tous les champs
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'input'
            })
            
        # Ajouter les placeholders pour les champs de base allauth
        self.fields['email'].widget.attrs.update({
            'placeholder': _('Votre email'),
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': _('Votre mot de passe'),
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': _('Confirmez votre mot de passe'),
        })

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user