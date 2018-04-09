from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from . import models
from . import forms

# Create your views here.
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    if request.session['user_id']:
        template_name = 'ratings/user.html'
        current_user = User.objects.get(userid=request.session['user_id'])        
        return render(request, template_name, {'user':current_user})
    #if not logged in redirect to url(/login)
    else:
        return redirect('ratings:login')

class LoginView(View):
    form_class = LoginForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def login(request):
        request.session['user_id'] = self.form_class.get_user_id()

class LogoutView(View):
    del request.session['user_id']
    return redirect('ratings:user_list')

class UserUpdate(UpdateView):
    model = models.User
    fields = ['name','about','updated_at']

class WorkUpdate(UpdateView):
    model = models.Work
    fields = ['user','work']

class UserDetailView(generic.DetailView):
    template_name = 'ratings/user.html'
    # Get ratings for this user, rated by the session user
    # Edit the user details if the user id of the current view is the same as the session user
    # Edit the work details if the user id of the current view is the same as the session user