from django.db import models
from errno import ENOTCONN
from telnetlib import GA
from django.core.mail import send_mail
from django_rest_passwordreset.signals import reset_password_token_created
from django.urls import reverse
from pyuploadcare.dj.models import ImageField
from email.policy import default
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail
from django.conf import settings

from django_otp.models import Device
from django_otp.plugins.otp_totp.models import TOTPDevice



class Gender(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=25)
    def __str__(self):
        return f'{self.name}'

class ProfileStatus(models.Model):
    date_created = models.DateTimeField(auto_now=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.name}'

class Profile(models.Model):
    date_modified = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    status = models.ForeignKey(ProfileStatus,blank=True, null=True, on_delete=models.CASCADE)
    date_of_birth =models.DateField(blank=True, null=True,)
    sex = models.ForeignKey(Gender,blank=True, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100,null=True, blank=True)
    profile_picture = ImageField(null=True, blank=True)
    otp_device = models.OneToOneField(TOTPDevice, null=True, blank=True, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    @classmethod
    def get_by_id(cls, id):
        profile = Profile.objects.get(user=id)
        return profile

    @classmethod
    def filter_by_id(cls, id):
        profile = Profile.objects.filter(user=id).all()
        return profile

class ImageUpload(models.Model):
    image= ImageField(null=True, blank=True)
    name = models.CharField(max_length=25)

    def __str__(self):
        return f'{self.name}'
