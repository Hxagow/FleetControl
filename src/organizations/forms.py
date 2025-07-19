from django import forms
from django_countries.fields import CountryField
from .models import Organization

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