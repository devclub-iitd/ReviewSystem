from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.views import generic
from django.views.generic import View

# Create your views here.
class IndexView(generic.ListView):
    template_name = 'ratings/index.html'

class UserCreate(CreateView):
    model = User
    fields = ['']