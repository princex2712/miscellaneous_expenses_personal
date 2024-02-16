from typing import Any
from django.contrib import admin
from .models import SuperUserModel,MembersModel

# Register your models here.
class SuperUserModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
admin.site.register(SuperUserModel,SuperUserModelAdmin)
admin.site.register(MembersModel)