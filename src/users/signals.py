from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from organizations.models import Invitation
from .models import OrganizationUser
from django.utils import timezone


@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    """
    Lier l'invitation au nouvel utilisateur sans l'ajouter automatiquement à l'organisation
    Les utilisateurs devront accepter explicitement l'invitation via les notifications
    """
    # Vérifier s'il y a un token d'invitation dans la session ou les paramètres
    invitation_token = None
    
    if request:
        # Essayer de récupérer le token depuis les paramètres GET
        invitation_token = request.GET.get('invitation')
        
        # Ou depuis la session si elle a été stockée
        if not invitation_token:
            invitation_token = request.session.get('invitation_token')
    
    if invitation_token:
        try:
            invitation = Invitation.objects.get(token=invitation_token)
            
            # Vérifier que l'invitation est valide et pour le bon email
            if invitation.can_be_accepted() and invitation.email == user.email:
                # L'invitation reste en attente - l'utilisateur pourra l'accepter via les notifications
                # Nettoyer la session
                if request and 'invitation_token' in request.session:
                    del request.session['invitation_token']
                    
                # Nettoyer les autres invitations expirées ou traitées pour cet email
                other_invitations = Invitation.objects.filter(
                    email=user.email
                ).exclude(id=invitation.id)
                
                for inv in other_invitations:
                    if inv.is_expired() or inv.status in ['accepted', 'declined']:
                        inv.delete()
                    
        except Invitation.DoesNotExist:
            pass  # Invitation invalide, ignorer
