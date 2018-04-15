from django import forms
from . import models

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = models.User
        fields = ('userid', 'password', 'name',  'about')


class RatingForm(forms.ModelForm):
    # if user1.canRate = 1 and edit if canEdit = 1
    class Meta:
        model = models.Rating
        # fields = ('user1', 'user2', 'rating')
        fields = ('rating', )

class WorkForm(forms.ModelForm):
    class Meta:
        model = models.Work
        fields = ('user', 'work')

# class LoginForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput)
    
#     class Meta:
#         model = models.User
#         fields = ('userid', 'password')


class LoginForm(forms.Form):
    userid = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    # class Meta:
    #     model = models.User
    #     fields = ('userid', 'password')