from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views

app_name = 'ratings'

urlpatterns = [
    path('', login_required(views.IndexView.as_view(template_name="ratings/user.html")), name='index'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html', 'extra_context':{'type':'Login','logged_in':False}}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', views.RegisterView.as_view() , name='register'),
    url(r'^user/(?P<uid>\w+)/$', views.UserDetailView.as_view(), name='detail'),
    url(r'^leaderboard/$', views.LeaderBoardView.as_view(), name='leaderboard'),
    url(r'^sudo/$', views.SudoView.as_view(), name='sudo'),
    url(r'^user/(?P<uid>\w+)/edit$',views.EditView.as_view(), name='editprofile')
    ]
