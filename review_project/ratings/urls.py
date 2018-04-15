from django.urls import path
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from . import views

app_name = 'ratings'

urlpatterns = [
    path('', login_required(views.IndexView.as_view(template_name="login.html")), name='index'),
    url(r'^login/$', auth_views.login, {'template_name': 'registration/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    # url(r'^login/$', views.LoginView.as_view() , name='login'),
    # url(r'^logout/$', views.LogoutView.as_view() , name='logout'),
    url(r'^register/$', views.RegisterView.as_view() , name='register'),
    url(r'user_list/$', views.UserListView.as_view(), name='user_list')
]