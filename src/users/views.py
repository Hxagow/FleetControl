from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.utils import timezone
from allauth.account.views import SignupView
from allauth.account.utils import complete_signup
from organizations.models import Invitation
from .models import Membership
from .forms import ProfileForm, CustomSignupForm


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil mis à jour avec succès.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'account/profile.html', {'form': form})


class InvitationSignupView(SignupView):
    """
    Vue d'inscription personnalisée qui gère les invitations
    """
    template_name = 'account/signup.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passer la request au formulaire
        kwargs['request'] = self.request
        return kwargs
    
    def get_initial(self):
        initial = super().get_initial()
        
        # Vérifier s'il y a un token d'invitation
        invitation_token = self.request.GET.get('invitation')
        if invitation_token:
            try:
                invitation = Invitation.objects.get(token=invitation_token)
                if invitation.can_be_accepted():
                    initial['email'] = invitation.email
                    # Stocker le token dans la session
                    self.request.session['invitation_token'] = str(invitation_token)
            except Invitation.DoesNotExist:
                pass
        
        return initial
    
    def form_valid(self, form):
        # Appeler la méthode parent pour créer l'utilisateur
        response = super().form_valid(form)
        
        # Le signal user_signed_up va automatiquement gérer l'invitation
        # grâce au token stocké en session
        
        return response


@login_required
def accept_invitation(request, invitation_id):
    """
    Accepter une invitation
    """
    invitation = get_object_or_404(Invitation, id=invitation_id, email=request.user.email)
    
    if not invitation.can_be_accepted():
        messages.error(request, "Cette invitation n'est plus valide.")
        return redirect('organizations_panel')
    
    # Accepter l'invitation
    invitation.status = 'accepted'
    invitation.responded_at = timezone.now()
    invitation.save()
    
    # Créer le membership
    Membership.objects.get_or_create(
        user=request.user,
        organization=invitation.organization,
        defaults={'role': 'member'}
    )
    
    # Supprimer l'invitation maintenant qu'elle est traitée
    invitation.delete()
    
    messages.success(request, f'Vous avez rejoint {invitation.organization.name} !')
    return redirect('organizations_panel')


@login_required
def decline_invitation(request, invitation_id):
    """
    Refuser une invitation
    """
    invitation = get_object_or_404(Invitation, id=invitation_id, email=request.user.email)
    
    if not invitation.can_be_accepted():
        messages.error(request, "Cette invitation n'est plus valide.")
        return redirect('organizations_panel')
    
    # Refuser l'invitation
    invitation.status = 'declined'
    invitation.responded_at = timezone.now()
    invitation.save()
    
    # Supprimer l'invitation maintenant qu'elle est traitée
    invitation.delete()
    
    messages.info(request, 'Invitation refusée.')
    return redirect('organizations_panel')



