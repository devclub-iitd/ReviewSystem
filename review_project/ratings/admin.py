from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(Profile)
admin.site.register(Work)
admin.site.register(Rating)
admin.site.register(Control)