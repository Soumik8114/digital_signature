from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserKeyPair

from .utils import generate_keys, encrypt_key,create_or_update_user_keys

@receiver(post_save, sender=User)
def create_user_key_pair(sender, instance, created, **kwargs):
    if created:
        create_or_update_user_keys(instance)