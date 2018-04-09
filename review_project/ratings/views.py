from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from . import models
from . import forms

# Create your views here.
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    def get(self, request):

        

        # if request.session['user_id']:
        if 'user_id' in request.session:
            template_name = 'ratings/user.html'
            try:
                current_user = models.User.objects.get(userid=request.session['user_id'])        
            except ObjectDoesNotExist:
                return render(request, 'ratings/error.html',{'error': "The User for user_id : "+request.session['user_id']+" DoesNotExist. "})

            # if current_user == None :
            #     return render(request, 'ratings/error.html',{'error': "User not found: "+ request.session.user_id})
                
            return render(request, template_name, {'user':current_user , 'current':True})
        #if not logged in redirect to url(/login)
        else:
            return redirect('ratings:login')

class LoginView(View):
    form_class = forms.LoginForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        return render(request, template_name, {'form':form})

    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid() :
            form.save()
            request.session['user_id'] = form.cleaned_data['userid']
            
            return redirect('ratings:index')

class LogoutView(View):
    def get(self, request):
        del request.session['user_id']
        return redirect('ratings:user_list')

class UserUpdate(generic.UpdateView):
    model = models.User
    fields = ['name','about','updated_at']

class WorkUpdate(generic.UpdateView):
    model = models.Work
    fields = ['user','work']

class UserDetailView(generic.DetailView):
     def get(self, request):
        template_name = 'ratings/user.html'
        try: 
            user = models.User.objects.get(userid=request.GET.get('user','None'))     
        except ObjectDoesNotExist:
                return render(request, 'ratings/error.html',{'error': "The User for user_id : "+request.session['user_id']+" DoesNotExist. "})
        return render(request, template_name, {'user':user , 'current':False})
        #if not logged in redirect to url(/login)
    # Get ratings for this user, rated by the session user
    # Edit the user details if the user id of the current view is the same as the session user
    # Edit the work details if the user id of the current view is the same as the session user