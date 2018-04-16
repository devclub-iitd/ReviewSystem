from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from . import models
from . import forms
import datetime

error_template = 'ratings/error.html'
login_template = 'ratings/login.html'
TIME_LIMIT = 2*86400 

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
                return render(request, error_template ,{'error': "The User for user_id : "+request.session['user_id']+" DoesNotExist. "})

            return render(request, template_name, {'user':current_user , 'current':True})
        #if not logged in redirect to url(/login)
        else:
            return redirect('ratings:login')

class LeaderBoardView(generic.ListView):
    model = models.User
    context_object_name = 'leaderboard'

class LoginView(View):
    form_class = forms.LoginForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        print("-----------------------------------------------------")
        print (form) # this turned out to be null
        
        return render(request, self.template_name, {'form':form,"type":"Login"})

    def post(self,request):
        form = self.form_class(request.POST)

        print("-----------------------------------------------------")
        print (form) # this turned out to be null
        # print (form.cleaned_data)
        # print (form.cleaned_data['userid'])
        # print (form.cleaned_data['password'])

        if form.is_valid() :
            # form.save()
            uid = form.cleaned_data['userid']
            paswd = form.cleaned_data['password']
            try: 
                uobj = models.User.objects.get(userid=uid)
                if(uobj):
                    if(uobj.password == paswd) : 
                        request.session['user_id'] = form.cleaned_data['userid']
                        return redirect('ratings:index')
                    else :
                        return render(request, self.template_name, {'error_message': "Password doesn't match"})
                else :
                    return render(request, self.template_name, {'form': form ,'error_message': "User doesn't exist."})
            except ObjectDoesNotExist : 
                return render(request, self.template_name, { 'form': form ,'error_message': "User ID doesn't exist."})

            return redirect('ratings:index')
        else : 
            print("-----------------------------------------------------")
            print (form)
            # print (request.session['user_id'])
            return redirect('ratings:login')

class LogoutView(View):
    def get(self, request):
        try: 
            if request.session['user_id']:
                del request.session['user_id']
        except Exception:
            pass
        return redirect('ratings:login')

class RegisterView(View):
    form_class = forms.UserForm
    template_name = 'ratings/login.html'
    # Add user id to session variables
    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form,'type':"Register"})

    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid() :
            # form.save()
            fd = form.cleaned_data
            uobj = models.User(name=fd['name'],userid=fd['userid'],about=fd['about'],
                                password=fd['password'],canSee=False,canRate=True)
            uobj.save()
            request.session['user_id'] = fd['userid']
            return redirect('ratings:index')
        else :
            return redirect('ratings:register')

class UserUpdate(generic.UpdateView):
    model = models.User
    fields = ['name','about','updated_at']

class WorkUpdate(generic.UpdateView):
    model = models.Work
    fields = ['user','work']

########################################## Do @ superuserloginrequired here ###################################
# @user_passes_test(lambda u: u.is_superuser)
class SudoView(View):
    form_class = forms.SudoForm
    template_name = 'ratings/sudo.html'
    # Add user id to session variables

    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form':form, 'type':"Sudo"})

    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid() :
            # form.save()
            ecs = form.cleaned_data['EveryoneCanSee']
            ecr = form.cleaned_data['EveryoneCanRate']
            ece = form.cleaned_data['EveryoneCanEdit'] # this has to make ratings editable over a certain timeframe .
            
            print("--------------------------------------------------------------")
            print(ecs, ecr, ece)
            print("--------------------------------------------------------------")
            
            userlist = models.User.objects.all()
            for user in  userlist:
                user.canSee  = ecs
                user.canRate = ecr
                user.save()

            ratings = models.Rating.objects.all()
            tnow = datetime.datetime.now()

            for rating in ratings :
                # find a better way than this because without
                print ("----------------------------------------------------------")  
                print ( abs ( rating.created_at.timestamp() - tnow.timestamp() ) )
                if abs ( rating.created_at.timestamp() - tnow.timestamp() ) <= TIME_LIMIT : 
                    rating.canEdit = ece
                    rating.save()

            # iterate over all users and make the required fields as such 

            return redirect(self.request.path_info)
        else : 
            print("-----------------------------------------------------")
            print (form)
            return render(request, error_template, {'error': "Your Sudo form wasn't valid. Now you are redirected to Error Page."})


class UserDetailView(generic.DetailView):
    form_class = forms.RatingForm
    template_name = 'ratings/user.html'

    def get(self, request,**kwargs):
        uid = kwargs['uid'] # target user
        raterid = request.session['user_id']

        if 'user_id' in request.session:
            try: 
                user = models.User.objects.get(userid=uid)
            except ObjectDoesNotExist:
                return render(request, error_template ,{'error': "The User for primary key : "+ uid +" does not exist."})

                # user = models.User.objects.get(userid=request.GET.get('user','None'))
            try:
                ratings = models.Rating.objects.all().filter(user1=raterid).filter(user2=user).order_by('-updated_at')
            except ObjectDoesNotExist:
                current_rating = "Not yet rated by you. Rating Object after these filters doesn't exist."
            try: 
                current_rating = ratings[0].rating
            except :
                current_rating = "Not yet rated by you."
            try : 
                works = models.Work.objects.all().filter(user=user).order_by('-updated_at')
            except :
                works = None

            rater = models.User.objects.get(userid = raterid)
            if rater.canRate :
                form = self.form_class(None)
            else  : 
                form = None    
            
            return render(request, self.template_name, {'user':user, 'current':False, 'current_rated':current_rating, 'works': works, 'form':form})
        
        else:
            # if not logged in redirect to url(/login)
            user = models.User.objects.get(userid=uid)
            try : 
                works = models.Work.objects.all().filter(user=user).order_by('-updated_at')
            except :
                works = None
            return render(request, self.template_name, {'user':user, 'current':False, 'works':works})
    
    def post(self, request, **kwargs):
        form = self.form_class(request.POST)

        # print("-----------------------------------------------------")
        # print (form)
        if 'user_id' in request.session :
            if form.is_valid() :
                rnum = form.cleaned_data['rating']
                rater = models.User.objects.get(userid = request.session['user_id'])
                target = models.User.objects.get(userid = kwargs['uid'])
                if kwargs['uid'] == None :
                    return render( request, self.template_name , {'error_message': "No kwargs in post request.", 'form':form} ) 
                elif kwargs['uid'] == request.session['user_id'] :
                    return render( request, self.template_name , {'error_message': "You cannot rate yourself.", 'form':form} )
                else :    
                    f = True 
                    try:
                        ratings = models.Rating.objects.all().filter(user1=rater).filter(user2=target).order_by('-updated_at')
                        robj = ratings[0]
                        if (not robj.canEdit) :
                            f = False
                    except :
                        f = False
                    
                    if f :
                        robj.rating =  rnum
                    else :
                        robj = models.Rating(user1 = rater,
                                            user2 = target,
                                            rating=rnum, canEdit = True)
                    robj.save()

                return redirect(self.request.path_info)
            else : 
                print("-----------------------------------------------------")
                print (form)
                # print (request.session['user_id'])
                return render( request, self.template_name , {'error_message': "Ratings form wan't valid.", 'form':form} ) 
        else :
            return render( request, login_template , {'error_message': "You have to be logged in to rate.", 'form':form} ) 
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

