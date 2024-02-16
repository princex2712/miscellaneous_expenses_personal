from django.db import models
from master.models import BaseClass
from authentication.models import MembersModel

# Create your models here.
class IncomeModel(BaseClass):
    member_id = models.ForeignKey(MembersModel,on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.DecimalField(default=0,decimal_places=2,max_digits=10)

    def __str__(self):
        return str(self.member_id)  