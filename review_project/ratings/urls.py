from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'ratings'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view() , name='login'),
    url(r'^logout/$', views.LogoutView.as_view() , name='logout'),
    url(r'^register/$', views.RegisterView.as_view() , name='register'),
    url(r'^user/(?P<uid>\w+)/$',views.UserDetailView.as_view() , name='detail'),
    url(r'^leaderboard/$', views.LeaderBoardView.as_view(), name='leaderboard'),
    url(r'^sudo/$', views.SudoView.as_view(), name='sudo')
]