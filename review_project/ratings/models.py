from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    userid = models.CharField(primary_key=True,max_length=6,unique=True)
    # password = models.CharField(max_length=256)
    # name = models.CharField(max_length=50)
    about = models.CharField(max_length=200)
    canSee = models.BooleanField()
    canRate = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    USERNAME_FIELD = 'userid'

    def __str__(self):
        return self.userid

class Rating(models.Model):
    #user1 rating to user2 
    user1  = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='Profile1')
    user2  = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='user2')
    rating = models.IntegerField()
    # timestamp=models.DateField()
    canEdit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Work(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    work = models.CharField(max_length=500)
    # timestamp = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    