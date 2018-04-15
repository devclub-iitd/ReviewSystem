from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User

class Profile(models.Model):
    userid = models.CharField(primary_key=True,unique=True,max_length=6,default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=200)
    canSee = models.BooleanField(default=True)
    canRate = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    # USERNAME_FIELD = 'userid'
    # REQUIRED_FIELDS = ('user')

    def __str__(self):
        return self.userid

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance,userid=instance.username)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Rating(models.Model):
    #user1 rating to user2 
    user1  = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='Profile1')
    user2  = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='Profile2')
    rating = models.IntegerField()
    # timestamp=models.DateField()
    canEdit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Work(models.Model):
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    work = models.CharField(max_length=500)
    # timestamp = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    