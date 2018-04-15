from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from . import models

class ProfileForm(UserCreationForm):
    about = forms.CharField(max_length=200)
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2')

class RatingForm(forms.ModelForm):
    # if user1.canRate = 1 and edit if canEdit = 1
    class Meta:
        model = models.Rating
        fields = ('user1', 'user2', 'rating')

class WorkForm(forms.ModelForm):
    class Meta:
        model = models.Work
        fields = ('user', 'work')

class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')