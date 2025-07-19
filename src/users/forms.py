from allauth.account.forms import SignupForm
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from organizations.models import Organization
from .models import Membership

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
        super().__init__(*args, **kwargs)
        if hasattr(self, 'request'):
            # Récupérer l'email depuis les paramètres GET
            email = self.request.GET.get('email')
            if email:
                self.fields['email'].initial = email
                self.fields['email'].widget.attrs['readonly'] = True

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user