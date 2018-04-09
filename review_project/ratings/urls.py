from django.urls import path

from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    url(r'^$', views.IndexView.as_view(), name='index')
]