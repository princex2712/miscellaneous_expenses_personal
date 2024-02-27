from django.db import models
from master.models import BaseClass
from authentication.models import MembersModel,SuperUserModel

# Create your models here.
class IncomeModel(BaseClass):
    superuser_id = models.ForeignKey(SuperUserModel,on_delete=models.CASCADE)
    member_id = models.ForeignKey(MembersModel,on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(default=0,decimal_places=2,max_digits=10)

    def __str__(self):
        return str(self.member_id)  

class Category(BaseClass):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Expenses(BaseClass):
    superuser_id = models.ForeignKey(SuperUserModel,on_delete=models.CASCADE)
    category_id=models.ForeignKey(Category,on_delete=models.CASCADE)
    member_id = models.ForeignKey(MembersModel,on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(default=0,decimal_places=2,max_digits=10)
    description = models.TextField(blank=True)