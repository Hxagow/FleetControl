from django import forms
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from .models import Organization, Invitation
from django.core.exceptions import ValidationError
from .validators import no_emoji_validator

class OrganizationForm(forms.ModelForm):
    # LANGUAGE_CHOICES = [
    #     ('fr', 'Français'),
    #     ('en', 'English'),
    #     ('de', 'Deutsch'),
    # ]
    
    country = CountryField().formfield(widget=forms.Select(attrs={'class': 'input bg-white'}))
    postal_code = forms.CharField(max_length=10, required=True)
    # language = forms.ChoiceField(
    #     choices=LANGUAGE_CHOICES,
    #     widget=forms.RadioSelect(attrs={'class': 'hidden peer'})
    # )
    
    class Meta:
        model = Organization
        fields = ['logo', 'name', 'description', 'phone', 'address', 'postal_code', 'city', 'country']

    def clean(self):
        cleaned_data = super().clean()

        fields_to_validate = ['name', 'phone', 'address', 'postal_code', 'city', 'country']

        for field in fields_to_validate:
            value = cleaned_data.get(field)
            if value in (None, ''):
                continue
            try:
                no_emoji_validator(value)
            except ValidationError as e:

                self.add_error(field, e)

        return cleaned_data


class InvitationForm(forms.Form):
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'placeholder': _('email@exemple.com'),
            'class': 'input'
        })
    )

    def __init__(self, *args, **kwargs):
        self.organization = kwargs.pop('organization', None)
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        
        # Vérifier s'il y a déjà une invitation en attente pour cet email
        if self.organization:
            # D'abord, nettoyer les invitations expirées
            expired_invitations = Invitation.objects.filter(
                email=email,
                organization=self.organization
            )
            for inv in expired_invitations:
                if inv.is_expired():
                    inv.delete()
            
            # Maintenant vérifier s'il reste une invitation en attente
            existing_invitation = Invitation.objects.filter(
                email=email,
                organization=self.organization,
                status='pending'
            ).first()
            
            if existing_invitation and not existing_invitation.is_expired():
                raise forms.ValidationError(_('Une invitation est déjà en attente pour cet email.'))
        
        return email