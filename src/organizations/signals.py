from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Invitation
from users.models import Membership

User = get_user_model()

@receiver(post_save, sender=User)
def handle_user_signup(sender, instance, created, **kwargs):
    if created:
        # Vérifier s'il y a une invitation en attente pour cet email
        invitation = Invitation.objects.filter(
            email=instance.email,
            accepted=False
        ).first()
        
        if invitation and not invitation.is_expired():
            # Créer l'adhésion
            Membership.objects.create(
                user=instance,
                organization=invitation.organization,
                role=invitation.role
            )
            # Marquer l'invitation comme acceptée
            invitation.accept() 