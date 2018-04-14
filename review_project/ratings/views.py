from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from . import models
from . import forms

# Create your views here.
# @login_required(login_url='/login/')
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    @method_decorator(login_required)
    def get(self, request):
        template_name = 'ratings/user.html'
        u = request.user
        print ("Entered Index")
        print (u.username)
        # cuser = {}
        # cuser['first_name','username','about','password'] = u.first_name, u.username, u.about, u.password
        # print (cuser[username])
        # UsrObj = Student(name=u.student.name, department=u.student.department,
        #     DP=u.student.DP,phone=u.student.phone,email=u.student.email,
        #     oneliner=u.student.oneliner,genPic1=u.student.genPic1,genPic2=u.student.genPic2)
        #     context={"user":UsrObj}
        # # print int(request.FILES.get('dp').size)<6000000
        # u.student.name = request.POST.get('name')
        # u.student.phone = request.POST.get('phone')
        # u.student.email = reqst.POST.get('email')
        # u.student.oneliner = request.POST.get('oneliner')
        # u.student.save()
        return render(request, template_name, {'user': u , 'current':True})
        
    def post(self, request):
        print ("Post request in index")
        u = request.user
        edits = {}
        edits['userid','password','name','about'] = request.POST.get('userid'), request.POST.get('password'), request.POST.get('name'), request.POST.get('about') 
        # now create a new user ?
        # edits['canSee','canRate'] = True, False 
        u.save(edits)

        return redirect('ratings:index')

class UserListView(generic.ListView):
    model = models.Profile
    context_object_name = 'user_list'

class RegisterView(View):
    form_class = forms.CustomUserCreationForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self,request):
        print ("Received Post Request")
        form = self.form_class(request.POST)

        if form.is_valid():
            # fd = form.cleaned_data
            # obj = models.Profile(username=fd['username'],password=fd['password'],about=fd['about'],canSee=True,canRate=True)
            form.save()
            return redirect('ratings:login')
        else:
            return render(request, self.template_name, {'form':form})

class LoginView(View):
    form_class = forms.LoginForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form})

    def post(self,request):
        # lowerUsername = (request.POST.get('userid')).lower()
        # print (lowerUsername)
        user = authenticate(username=request.POST['username'],password=request.POST['password'])
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

class UserUpdate(generic.UpdateView):
    model = models.Profile
    fields = ['name','about','updated_at','work']

class UserDetailView(generic.DetailView):
    @login_required()
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