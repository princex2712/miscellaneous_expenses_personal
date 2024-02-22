from django.contrib import admin
from .models import IncomeModel,Category,Expenses

# Register your models here.
admin.site.register(IncomeModel)
admin.site.register(Category)
admin.site.register(Expenses)