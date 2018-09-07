from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core import signing
import datetime

def decrypt(encryptedqueryset,string='work'):
    dictionary=encryptedqueryset.values(string)
    trueworks=[]
    for i in dictionary:
        m=i.get(string)
        trueworks.append(m)
    decryptworks=[]
    for i in trueworks:
        n=signing.loads(i)
        decryptworks.append(n[0])
    return decryptworks

class Profile(models.Model):
    userid = models.CharField(primary_key=True,unique=True,max_length=6,default='')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=200)
    can_see = models.BooleanField(default=True)
    can_rate = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    current_rating = models.FloatField(default=0.0,validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])
    cumulated_rating = models.FloatField(default=0.0,validators=[MinValueValidator(0.0), MaxValueValidator(10.0)])

    # ImageField¶ While adding profile pictures
    # class ImageField(upload_to=None, height_field=None, width_field=None, max_length=100, **options)

    def __str__(self):
        return self.userid


    def updateMyRating(self):
        # tnow = datetime.datetime.now()

        # A control object must be present
        recent_control = (Control.objects.all().order_by('-updated_at'))[0]
        recent_session_number = recent_control.session_number
        threshold = recent_control.threshold_persons

        current_ratings_list = Rating.objects.all().filter(user2 = self.userid).filter(session_number = recent_session_number) # ratings to our user

        # to calculate total ratings
        total_num_ratings = 0
        cumulative_rating = 0.0

        # to calculate this session's ratings
        recent_ratings = 0
        current_rating = 0.0

        for rating in current_ratings_list :
            #decrypt it here
            encrypted_rating = rating.rating
            decrypted_rating = signing.loads(encrypted_rating)
            rate = decrypted_rating[0]
            #cumulative_rating += r.rating
            cumulative_rating += rate
            total_num_ratings += 1

            if rating.session_number == recent_session_number :
                current_rating += rate
                recent_ratings += 1

        
        #  if Divide by zero because of no ratings 
        total_num_ratings = (total_num_ratings > 0 ) ? total_num_ratings : 1
        recent_ratings    = (recent_ratings    > 0 ) ? recent_ratings    : 1 

        self.current_rating   = (current_rating / recent_ratings )
        self.cumulated_rating = (cumulative_rating / total_num_ratings )

        num_current_rated = Rating.objects.all().filter(user1 = self.userid).filter(session_number = recent_session_number).count()
        num_users = User.objects.all().exclude(is_superuser=True).count()
        
        # person has rated less than threshold then don't allow to see
        self.can_see = ( num_current_rated < threshold ) ? False : True 

    def get_absolute_url(self):
        return ("/user/"+self.userid)

    def get_latest_work(self):
        works = Work.objects.filter(user=self).order_by('-updated_at').values('work')
        trueworks=[]
        
        for work in works:
            data = work.get('work')
            trueworks.append(data)
        works = trueworks

        try:
            latest_work = works[0]
            decrypted_work = signing.loads(latest_work)
            return decrypted_work[0]
        except:
            return None

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance,userid=instance.username)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

class Rating(models.Model):
    # Session number for versioning
    session_number = models.IntegerField(default=0)
    
    #user1 rating to user2
    user1   = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='Profile1')
    user2   = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name='Profile2')
    
    # Integer field before
    #rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Changed because now encrypted char field
    rating  = models.CharField(max_length=100)
    review  = models.CharField(max_length=1024)
    
    can_edit = models.BooleanField() # Is the rating editable 

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (self.user1.userid + " rated " + self.user2.userid)

class Work(models.Model):
    user = models.ForeignKey(Profile,on_delete=models.CASCADE)
    work = models.CharField(max_length=500,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.work

class Control(models.Model):

    # Control fields
    session_number = models.IntegerField(default=0)
    registration_enabled = models.BooleanField(default=True)
    everyone_can_see  = models.BooleanField(default=True)
    everyone_can_rate = models.BooleanField(default=True)
    everyone_can_edit = models.BooleanField(default=True) # doesn't overwrite 
    update_everyone  = models.BooleanField(default=True)

    threshold_persons = models.PositiveIntegerField(default=0)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def updateOthers(self):
        userlist = Profile.objects.all()
        for user in  userlist:
            # can see and rate overwritten before
            user.can_see  = self.everyone_can_see
            user.can_rate = self.everyone_can_rate
            if self.update_everyone :
                user.update_ratings()
            user.save()

        ratings = Rating.objects.all()

        for rating in ratings :
            # if abs ( rating.created_at.timestamp() - tnow.timestamp() ) <= self.TimeLimitForRatingEdits :
            if rating.session_number == self.session_number : 
                rating.can_edit = self.everyone_can_edit
                rating.save()

    def __str__(self):
        return (str(self.session_number))
