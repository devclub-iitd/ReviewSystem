from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'ratings'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^login/$', views.LoginView.as_view() , name='login'),
    url(r'user_list/$', views.UserListView.as_view(), name='user_list')
]