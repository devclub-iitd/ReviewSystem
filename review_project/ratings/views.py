from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from . import models
from . import forms

# Create your views here.
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    @login_required()
    def get(self, request):
        template_name = 'ratings/user.html'


        u = request.user
        cuser = {}
        cuser['name','userid','about','password'] = u.name, u.userid, u.about, u.password


        # UsrObj = Student(name=u.student.name, department=u.student.department,
        #     DP=u.student.DP,phone=u.student.phone,email=u.student.email,
        #     oneliner=u.student.oneliner,genPic1=u.student.genPic1,genPic2=u.student.genPic2)
        #     context={"user":UsrObj}
        # # print int(request.FILES.get('dp').size)<6000000
        # u.student.name = request.POST.get('name')
        # u.student.phone = request.POST.get('phone')
        # u.student.email = request.POST.get('email')
        # u.student.oneliner = request.POST.get('oneliner')
        # u.student.save()
        return render(request, template_name, {'user': cuser , 'current':True})
        
        
        def post(self, request):
            pass


class UserListView(generic.ListView):
    model = models.User
    context_object_name = 'user_list'

class LoginView(View):
    form_class = forms.LoginForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self,request):
        	lowerUsername = (request.POST.get('username')).lower()
            user = authenticate(request,username=lowerUsername,password=request.POST.get('password'))
            if (user is not None):
                login(request,user)
                return redirect('ratings:index')
            else:
                return redirect('ratings:login')
        # form = self.form_class(request.POST)
        # if form.is_valid() :
        #     form.save()
        #     request.session['user_id'] = form.cleaned_data['userid']
        #     return redirect('ratings:index')



class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('ratings:list')
        # del request.session['user_id']
        # return redirect('ratings:user_list')

# @login_required()
class UserUpdate(generic.UpdateView):
    model = models.User
    fields = ['name','about','updated_at','work']

# class WorkUpdate(generic.UpdateView):
#     model = models.Work
#     fields = ['user','work']

class UserDetailView(generic.DetailView):
    
    # @login_required()
    def get(self, request):

        # u = request.user
        # cuser = 
        # return render(request, 'myapp/profile.html',context)

        if 'user_id' in request.session:
            template_name = 'ratings/user.html'
            try: 
                user = models.User.objects.get(userid=request.GET.get('user','None'))
                ratings = models.Rating.objects.all().filter(user1=request.session['user_id']).filter(user2=user).order_by('-updated_at')
                current_rating = ratings[0].rating
                works = models.Work.objects.all().filter(user=user).order_by('-updated_at')
            except ObjectDoesNotExist:
                return render(request, 'ratings/error.html',{'error': "The User for user_id : "+request.session['user_id']+" does not exist."})
            return render(request, template_name, {'user':user, 'current':False, 'current_rated':current_rating, 'works':works})
        else:
            # if not logged in redirect to url(/login)
            return redirect('ratings:login')  
    # Get ratings for this user, rated by the session user
    # Edit the user details if the user id of the current view is the same as the session user
    # Edit the work details if the user id of the current view is the same as the session user

    # Function to check if the user id of the current view is the same as the session user
    def is_same_user(self,request):
        if 'user_id' in request.session:
            user = models.User.objects.get(userid=request.GET.get('user','None'))
            return (user.userid==request.session['user_id'])
        else:
            return False  