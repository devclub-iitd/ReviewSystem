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
from django.core import signing


error_template = 'ratings/error.html'
login_template = 'registration/login.html'

# SESSION_NUMBER = 0

# Create your views here.
# @login_required(login_url='/login/')
class IndexView(generic.ListView):
    #if logged in, display the current user's details
    @method_decorator(login_required)
    def get(self, request):
        template_name = 'ratings/user.html'
        user = request.user

        try:
            current_user = models.Profile.objects.get(userid=user.profile.userid)
        except ObjectDoesNotExist:
            return render(request, error_template ,{'error': "The User for user_id : "+user.profile.userid+" DoesNotExist. "})
        # return render(request, template_name, {'user':current_user , 'current':True})
        return redirect('/user/'+user.profile.userid)

class LeaderBoardView(View):
    template_name = 'ratings/profile_list.html'

    @method_decorator(login_required)
    def get(self,request):
        object_list = models.Profile.objects.all().order_by('-current_rating')
        #ln=0
        #lst=[]
        ratercansee = request.user.profile.canSee
        logged_in=True
        loshortworks=[]
        for i in object_list:
            latest_work = i.get_latest_work()
            try:
                if len(latest_work)>40:
                    loshortworks.append(latest_work[:40])
                else:
                    loshortworks.append(None)
            except:
                loshortworks.append(latest_work)
        dict =[]
        for j in range(len(object_list)):
            if object_list[j].user.is_superuser:
                continue
            else:
                ele = {'profile':object_list[j],'short':loshortworks[j]}
                dict.append(ele)

        return render(request, self.template_name, {'dict':dict,'object_list':object_list,'ratercansee':ratercansee,'logged_in':logged_in,'loshortworks':loshortworks})

    # def get_context_data(self, **kwargs):
    #     ctx = super(LeaderBoardView, self).get_context_data(**kwargs)
    #     ctx['ratercansee'] = self.get_object().date.strftime("%B")
    #     return ctx

class RegisterView(View):
    form_class_profile = forms.ProfileForm
    template_name = 'registration/login.html'
    logged_in = False

    def get(self,request):
        # Assume the control object is available
        ctrl_latest = models.Control.objects.latest('updated_at')
        # Don't send a form profie if registration is disabled
        form_profile = self.form_class_profile(None) if ctrl_latest.registration_enabled else None 

        return render(request, self.template_name, {'form':form_profile, "type":"Register", 'logged_in':self.logged_in, 'registration':registration})

    def post(self,request):
        form_profile = self.form_class_profile(request.POST)

        if form_profile.is_valid():
            user = form_profile.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.profile.about = form_profile.cleaned_data.get('about')
            user.save()
            raw_password = form_profile.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('ratings:index')
        else:
            return render(request, self.template_name, {'form':form_profile,"type":"Register",'logged_in':self.logged_in})

class UserUpdate(generic.UpdateView):
    model = models.Profile
    fields = ['name', 'about', 'updated_at', 'work']

########################################## Do @ superuserloginrequired here ###################################
class SudoView(View):
    form_class = forms.SudoForm
    template_name = 'registration/login.html'
    # Add user id to session variables
    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/login/'))
    def get(self, request):
        logged_in = True
        try :
            ctrl = (models.Control.objects.all().order_by('-updated_at'))[0]
            registration = ctrl.RegistrationEnabled
        except :
            ctrl = models.Control()
            registration = True
        form = self.form_class(instance=ctrl)

        return render(request, self.template_name, {'registration':registration,'logged_in':logged_in,'form':form, 'type':"Sudo"})

    @method_decorator(user_passes_test(lambda u: u.is_superuser,login_url='/login/'))
    def post(self,request):
        form = self.form_class(request.POST)

        if form.is_valid() :
            SessionNumber = form.cleaned_data['SessionNumber']
            # commit = False ?

            latest_ctrl = models.Control.objects.latest('updated_at')
            
            #if same SessionNumber,then delete current object and create new
            if (latest_ctrl is not None) and (SessionNumber == latest_ctrl.session_number):
                latest_ctrl.delete()

            registration_enabled=form.cleaned_data['registration_enabled']
            everyone_can_rate=form.cleaned_data['everyone_can_rate']
            everyone_can_edit=form.cleaned_data['everyone_can_edit']
            update_everyone=form.cleaned_data['update_everyone']

            ctrl = models.Control(session_number=SessionNumber,registration_enabled=registration_enabled,
            everyone_can_edit=everyone_can_edit,everyone_can_rate=everyone_can_rate,update_everyone=update_everyone)

            ctrl.save()
            ctrl.updateOthers()

            # idk why but just do it
            return redirect(self.request.path_info)
        else :
            return render(request, self.template_name, {'logged_in':logged_in,'form':form, 'type':"Sudo", 'error_message': "Your Sudo form wasn't valid."})


class UserDetailView(generic.DetailView):
    form_class = forms.RatingForm
    form_class_work = forms.WorkForm
    form_class_update = forms.UserUpdateForm
    template_name = 'ratings/user.html'

    @method_decorator(login_required)
    def get(self, request, **kwargs):
        logged_in = True

        def decrypt(encryptedqueryset, string='work'):
            dictionary = encryptedqueryset.values(string)
            trueworks = []
            for i in dictionary:
                m = i.get(string)
                trueworks.append(m)
            decryptworks = []
            for i in trueworks:
                n = signing.loads(i)
                decryptworks.append(n[0])
            return decryptworks

        uid = kwargs['uid'] # target user
        if request.user:
            raterid = request.user.profile.userid
            ratingFound = False
            try:
                user_profile = models.Profile.objects.get(userid=uid)
                user = models.User.objects.get(username=uid)
                full_name = user.first_name + " " + user.last_name
            except ObjectDoesNotExist:
                # Invalid username in get request
                return render(request, error_template, {'error': "The User with User Id : "+ uid +" does not exist."})

            try:
                ratings = models.Rating.objects.all().filter(user1=raterid).filter(user2=user_profile).order_by('-updated_at')[:1]
                curr_control = models.Control.objects.latest('-updated_at')
                if curr_control.session_number == ratings.session_number:
                    current_review = decrypt(ratings, 'review')[0]
                    current_rating = decrypt(ratings, 'rating')[0]
                    ratingFound = True
                else:
                    raise Exception
            except:
                # Either first time rate or no rating in present session
                current_rating = "Not yet reviewed by you."
                current_review = "Not yet reviewed by you."

            try:
                works = models.Work.objects.all().filter(user=user_profile).order_by('-updated_at') #.values('work')
                decrypted_works = decrypt(works) # Works now consist of a list of decrypted works
            except:
                decrypted_works = None

            rater = models.Profile.objects.get(userid=raterid)
            if rater.can_rate:
                form = self.form_class(None)
            else:
                form = None

            # Get User Update Forms
            form_work = self.form_class_work(None) if (uid == raterid) else None
            form_update = self.form_class_update(initial={'about':rater.about}) if (uid == raterid) else None
            ratingFound = False if (uid == raterid) else ratingFound
            current = True if (uid == raterid) else False   # If on your own profile

            all_ratings = []
            if(current):
                curr_ratings = models.Rating.objects.filter(user2=rater).order_by('-updated_at')
                try:
                    reviews = decrypt(curr_ratings, 'review')
                    ratings = decrypt(curr_ratings, 'rating')
                    for j in range(len(reviews)):
                        all_ratings.append({'rating':ratings[j], 'review':reviews[j]})
                except:
                    reviews = None
                    ratings = None
            return render(request, self.template_name, {'logged_in':True, 'works_together':decrypted_works, 'user':user, 'name':full_name, 'current':current, 'current_rated':current_rating, 'works': works, 'ratingFound':ratingFound, 'form':form, 'workform':form_work, 'updateform':form_update, 'together':together, 'rater':rater,'current_review':current_review})
        else:
            return render(request, error_template, {'error': "No such user exists. Please validate your request."})


    def post(self, request, **kwargs):
        form = self.form_class(request.POST)
        workform = self.form_class_work(request.POST)
        updateform = self.form_class_update(request.POST)
        logged_in=True
        # avoid insecure access through postman
        try:
            target = models.Profile.objects.get(userid = kwargs['uid'])
            target_user = models.User.objects.get(username = kwargs['uid'])
            full_name = target_user.first_name + " " + target_user.last_name
        except:
            return render(request, error_template ,{'error': "Invalid Post Request."})
        if request.user :
            if form.is_valid() :
                rnum = form.cleaned_data['rating']
                rev = form.cleaned_data['review']
                encryptedreview=signing.dumps((rev,))
                rater = models.Profile.objects.get(userid = request.user.profile.userid)
                full_name = target_user.first_name + " " + target_user.last_name
                if kwargs['uid'] == None :
                    return render( request, self.template_name , {'error_message': "Invalid User", 'form':form, 'user':target, 'name':full_name} )
                elif kwargs['uid'] == request.user.profile.userid :
                    return render( request, self.template_name , {'error_message': "You cannot rate yourself.", 'form':form, 'user':target, 'name':full_name} )
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
                        robj.review = encryptedreview
                    else :
                        robj = models.Rating(user1 = rater,
                                            user2 = target,
                                            rating=rnum,review=encryptedreview, canEdit = True)
                    robj.save()
                return redirect(self.request.path_info)
            elif updateform.is_valid() :
                about = updateform.cleaned_data['about']
                user = models.Profile.objects.get(userid = request.user.profile.userid)
                user.about = about
                user.save()
                return redirect(self.request.path_info)

            elif workform.is_valid() :
                onlychoices=request.POST.getlist('working[]') # Returns list of selected checkbox(decrypted)
                work = workform.cleaned_data['work']
                tupwork= (work,)
                cryptotuple=signing.dumps(tupwork)
                #decryptotuple=signing.loads(cryptotuple)
                user = models.Profile.objects.get(userid = request.user.profile.userid)

                if work:
                    new_work = models.Work(user = user, work = cryptotuple)
                    new_work.save()
                if onlychoices:
                    for each_delete in onlychoices:
                            r=models.Work.objects.filter(user=user)
                            works=r.values('work')
                            trueworks=[]
                            for i in works:
                                m=i.get('work')
                                trueworks.append(m)
                            works=trueworks
                            for i in range(len(works)):
                                n=signing.loads(works[i])
                                if each_delete==n[0]:
                                    r[i].delete()
                                    break
                return redirect(self.request.path_info)

            else :
                # print (request.session['user_id'])
                return render( request, self.template_name , {'error_message': "Ratings form wan't valid.", 'form':form, 'user':target_user, 'name':full_name} )
        else :
            return render( request, login_template , {'error_message': "You have to be logged in to rate.", 'form':form, 'user':target_user, 'name':full_name} )
    # Get ratings for this user, rated by the session user
    # Edit the user details if the user id of the current view is the same as the session user
    # Edit the work details if the user id of the current view is the same as the session user

    # Function to check if the user id of the current view is the same as the session user
    def is_same_user(self,request):
        if request.user:
            user = models.User.objects.get(userid=request.GET.get('user','None'))
            return (user.userid==request.user.profile.userid)
        else:
            return False
