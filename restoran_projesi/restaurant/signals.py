# import django.apps
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Kullanici 

# @receiver(post_save, sender=django.apps.apps.get_model('restaurant', 'Kullanici'))
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
        
#         Kullanici.objects.create(user=instance)

