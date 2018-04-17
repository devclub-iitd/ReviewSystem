from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator 
import datetime

TIME_BUFF = 7 * 86400 

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    userid = models.CharField(primary_key=True,max_length=6,unique=True)
    about = models.CharField(max_length=200)
    password = models.CharField(max_length=256)

    canSee = models.BooleanField(default=True)
    canRate = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    current_rating = models.PositiveIntegerField(MaxValueValidator(10),default=0)
    cumulated_rating = models.PositiveIntegerField(MaxValueValidator(10),default=0)

    def __str__(self):
        return self.userid
        # gets current rating of the user , shouldn't we make this a field ? 
    def update_ratings(self):
        tnow = datetime.datetime.now()
        rl = Rating.objects.all().filter(user2 = self.userid) # ratings to our user
        
        totalRatings = 0
        cum_rating = 0.0
        recentRatings = 0
        cur_rating = 0.0

        for r in rl :
            cum_rating += r.rating
            totalRatings += 1 

            if abs( r.created_at.timestamp() - tnow.timestamp() ) <= TIME_BUFF :
                cur_rating += r.rating
                recentRatings += 1
        try : # if Divide by zero because of no ratings ?
            self.current_rating   = (int)(cur_rating / recentRatings)
            self.cumulated_rating = (int)(cum_rating / totalRatings )
        except : 
            self.current_rating   = 0
            self.cumulated_rating = 0
    
    def get_absolute_url(self):
        return ("/user/"+self.userid)


class Rating(models.Model):
    user1  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user1')
    user2  = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user2')
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    review = models.CharField(max_length=1024)

    canEdit = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.user1.userid + " rated " + self.user2.userid)
    
class Work(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    work = models.CharField(max_length=500)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.work
    