from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Profile)


class ProfileStatusAdmin(admin.ModelAdmin):
    	list_display = ('id','name','date_created','date_modified')
admin.site.register(ProfileStatus, ProfileStatusAdmin)

class GenderAdmin(admin.ModelAdmin):
    	list_display = ('id','name','date_created','date_modified')
admin.site.register(Gender, GenderAdmin)