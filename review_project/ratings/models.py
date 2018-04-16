from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    userid = models.CharField(primary_key=True,max_length=6,unique=True)
    about = models.CharField(max_length=200)
    password = models.CharField(max_length=256)

    canSee = models.BooleanField()
    canRate = models.BooleanField()
    updated_at = models.DateTimeField(auto_now=True)
    # current_rating = models.PositiveIntegerField(MaxValueValidator(10))
    # cumulated_rating = models.PositiveIntegerField(MaxValueValidator(10))

    def __str__(self):
        return self.userid
        # gets current rating of the user , shouldn't we make this a field ? 
    # def get_current_rating(self, request):
    #     pass 
    # def get_cumulative_rating(self, request):
    #     pass

class Rating(models.Model):
    user1  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user1')
    user2  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user2')
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    canEdit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return (self.user1.userid + " rated " + self.user2.userid)
    
class Work(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    work = models.CharField(max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return (self.user.userid+" 's work. ")
    