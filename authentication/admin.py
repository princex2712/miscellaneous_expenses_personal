from django.contrib import admin
from .models import SuperUserModel,MembersModel

# Register your models here.
admin.site.register(SuperUserModel)
admin.site.register(MembersModel)