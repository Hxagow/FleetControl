from django import forms
from django_countries.fields import CountryField
from .models import Organization
from users.models import Membership

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
        fields = ['name', 'description', 'logo', 'phone', 'address', 'postal_code', 'city', 'country']

class InvitationForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'input-base', 'placeholder': 'email@example.com'})
    )
    role = forms.ChoiceField(
        choices=Membership.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'input-base'})
    )