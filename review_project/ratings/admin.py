from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile,Work,Rating

# Register your models here.
admin.site.register(Profile)
admin.site.register(Work)
admin.site.register(Rating)