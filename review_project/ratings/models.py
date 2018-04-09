from django.db import models

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    userid = models.CharField(primary_key=True,min_length=6,max_length=6)
    about = models.CharField(max_length=200)
    password = models.CharField(max_length=256)
    
    canSee = models.BooleanField()
    canRate = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.userid

class Rating(models.Model):
    user1  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user1')
    user2  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user2')
    rating = models.IntegerField()
    # timestamp=models.DateField()
    canEdit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Work(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    work = models.CharField(max_length=500)
    # timestamp = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    