from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from . import models
from . import forms
import datetime

error_template = 'ratings/error.html'
login_template = 'ratings/login.html'
TIME_LIMIT = 2*86400 

# Create your views here.
# @login_required(login_url='/login/')
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    @method_decorator(login_required)
    def get(self, request):
        # if request.session['user_id']:
        if 'user_id' in request.session:
            template_name = 'ratings/user.html'
            userid = request.session['user_id']
            try:
                current_user = models.User.objects.get(userid=request.session['user_id'])        
            except ObjectDoesNotExist:
                return render(request, error_template ,{'error': "The User for user_id : "+request.session['user_id']+" DoesNotExist. "})

            # return render(request, template_name, {'user':current_user , 'current':True})
            return redirect('/user/'+userid)
        #if not logged in redirect to url(/login)
        else:
            return redirect('ratings:login')

class LeaderBoardView(generic.ListView):
    model = models.User
    context_object_name = 'leaderboard'
    ordering = ['-current_rating']

class RegisterView(View):
    form_class_profile = forms.ProfileForm
    template_name = 'registration/login.html'
    def get(self,request):
        form_profile = self.form_class_profile(None)
        return render(request, self.template_name, {'form':form_profile,"type":"Login"})

    def post(self,request):
        print ("Received Post Request")
        form_profile = self.form_class_profile(request.POST)

        if form_profile.is_valid():
            form_profile.save()
            username = form_profile.cleaned_data.get('username')
            raw_password = form_profile.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            print ("Logged in")
            return redirect('ratings:index')
        else:
            return render(request, self.template_name, {'userform':form_user,'profileform':form_profile})

# ---------------------------------Redundant Classes-------------------------------------
# class LoginView(View):
#     form_class = forms.LoginForm
#     template_name = 'ratings/login.html'
#     # Add user id to session variables
#     def get(self,request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form':form})
        # print("-----------------------------------------------------")
        # print (form) # this turned out to be null
        # # print (form.cleaned_data)
        # # print (form.cleaned_data['userid'])
        # # print (form.cleaned_data['password'])

        # if form.is_valid() :
        #     # form.save()
        #     uid = form.cleaned_data['userid']
        #     paswd = form.cleaned_data['password']
        #     try: 
        #         uobj = models.User.objects.get(userid=uid)
        #         if(uobj):
        #             if(uobj.password == paswd) : 
        #                 request.session['user_id'] = form.cleaned_data['userid']
        #                 return redirect('ratings:index')
        #             else :
        #                 return render(request, self.template_name, {'form': form ,'error_message': "Password doesn't match","type":"Login"})
        #         else :
        #             return render(request, self.template_name, {'form': form ,'error_message': "User doesn't exist.","type":"Login"})
        #     except ObjectDoesNotExist : 
        #         return render(request, self.template_name, { 'form': form ,'error_message': "User ID doesn't exist.","type":"Login"})

        #     return redirect('ratings:index')
        # else : 
        #     print("-----------------------------------------------------")
        #     print (form)
        #     # print (request.session['user_id'])
        #     return redirect('ratings:login')

# class LogoutView(View):
#     def get(self, request):
#         try: 
#             if request.session['user_id']:
#                 del request.session['user_id']
#         except Exception:
#             pass
#         return redirect('ratings:login')

# class RegisterView(View):
#     form_class = forms.UserForm
#     template_name = 'ratings/login.html'
#     # Add user id to session variables
#     def get(self,request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form':form,'type':"Register"})

#     def post(self,request):
#         form = self.form_class(request.POST)

#         if form.is_valid() :
#             # form.save()
#             fd = form.cleaned_data
#             uobj = models.User(name=fd['name'],userid=fd['userid'],about=fd['about'],
#                                 password=fd['password'],canSee=False,canRate=True)
#             uobj.save()
#             request.session['user_id'] = fd['userid']
#             return redirect('ratings:index')
#         else :
#             return redirect('ratings:register')

#     def post(self,request):
#         username = request.POST['username']
#         password = request.POST['password']
#         print (username)
#         print (password)
#         user = User.objects.filter(username=request.POST['username'],password=request.POST['password'])
#         if (user is not None):
#             login(request,user)
#             return redirect('ratings:index')
#         else:
#             print ("User is not found")
#             return redirect('ratings:login')

# class LogoutView(View):
#     def get(self, request):
#         logout(request)
#         return redirect('ratings:user_list')

class UserUpdate(generic.UpdateView):
    model = models.Profile
    fields = ['name','about','updated_at','work']

########################################## Do @ superuserloginrequired here ###################################
class SudoView(View):
    form_class = forms.SudoForm
    template_name = 'ratings/login.html'
    # Add user id to session variables

    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/login/'))
    def get(self,request):
        form = self.form_class(None)
        print (request.user.username)
        print (request.user.is_superuser)
        return render(request, self.template_name, {'form':form, 'type':"Sudo"})

    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/login/'))
    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid() :
            # form.save()
            ecs = form.cleaned_data['EveryoneCanSee']
            ecr = form.cleaned_data['EveryoneCanRate']
            ece = form.cleaned_data['EveryoneCanEdit'] # this has to make ratings editable over a certain timeframe .
            upd = form.cleaned_data['UpdateEveryone']
            
            userlist = models.User.objects.all()
            for user in  userlist:
                user.canSee  = ecs
                user.canRate = ecr
                if upd :
                    user.update_ratings()
                user.save()

            ratings = models.Rating.objects.all()
            tnow = datetime.datetime.now()

            for rating in ratings :
                # find a better way than this because without
                print ( abs ( rating.created_at.timestamp() - tnow.timestamp() ) )
                if abs ( rating.created_at.timestamp() - tnow.timestamp() ) <= TIME_LIMIT : 
                    rating.canEdit = ece
                    rating.save()

            return redirect(self.request.path_info)
        else : 
            # print (form)
            return render(request, error_template, {'error': "Your Sudo form wasn't valid. Now you are redirected to Error Page."})


class UserDetailView(generic.DetailView):
    form_class = forms.RatingForm
    form_class_work = forms.WorkForm
    form_class_update = forms.UserUpdateForm
    template_name = 'ratings/user.html'

    @login_required()
    def get(self, request,**kwargs):
        uid = kwargs['uid'] # target user
        if 'user_id' in request.session:
            raterid = request.session['user_id']
            ratingFound = False
            try: 
                user = models.User.objects.get(userid=uid)
            except ObjectDoesNotExist:
                return render(request, error_template ,{'error': "The User for primary key : "+ uid +" does not exist."})
            try:
                ratings = models.Rating.objects.all().filter(user1=raterid).filter(user2=user).order_by('-updated_at')
            except ObjectDoesNotExist:
                current_rating = "Not yet rated by you. Rating Object after these filters doesn't exist."
            try: 
                current_rating = ratings[0]
                ratingFound = True
            except :
                current_rating = "Not yet reviewed by you."
            try : 
                works = models.Work.objects.all().filter(user=user).order_by('-updated_at')
            except :
                works = None

            rater = models.User.objects.get(userid = raterid)
            if rater.canRate :
                form = self.form_class(None)
            else  : 
                form = None
            if raterid == uid :
                form_work = self.form_class_work(None)
                form_update = self.form_class_update(initial={'about':rater.about})
            else :
                form_work = None
                form_update = None                
            
            ratingFound = False if (uid == raterid) else ratingFound 
            current = True if (uid == raterid) else False
            return render(request, self.template_name, {'user':user, 'current':current, 'current_rated':current_rating, 'works': works, 'ratingFound':ratingFound, 'form':form, 'workform':form_work, 'updateform':form_update})
        
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
        workform = self.form_class_work(request.POST)
        updateform = self.form_class_update(request.POST)
        print(form)
        print(workform)
        print(updateform)
        if 'user_id' in request.session :
            if form.is_valid() :
                rnum = form.cleaned_data['rating']
                rev = form.cleaned_data['review']
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
                        robj.rating = rnum
                        robj.review = rev
                    else :
                        robj = models.Rating(user1 = rater,
                                            user2 = target,
                                            rating=rnum,review=rev, canEdit = True)
                    robj.save()
                return redirect(self.request.path_info)
            elif workform.is_valid() :
                work = workform.cleaned_data['work']
                user = models.User.objects.get(userid = request.session['user_id'])                
                new_work = models.Work(user = user, work = work)
                new_work.save()                
                return redirect(self.request.path_info)
            elif updateform.is_valid() :
                about = updateform.cleaned_data['about']
                user = models.User.objects.get(userid = request.session['user_id'])   
                user.about = about
                user.save()                
                return redirect(self.request.path_info)
            else : 
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

