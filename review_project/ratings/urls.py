from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    url(r'login/$', views.LoginView.as_view() , name='login'),
    url(r'user_list/$', views.UserListView.as_view(), name='user_list')
    
]