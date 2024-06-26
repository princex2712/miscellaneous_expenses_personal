from django.db import models
from master.models import BaseClass
from authentication.models import MembersModel,SuperUserModel
from PIL import Image

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
    description = models.TextField(default="--")

    def __str__(self):
        return f"{self.member_id.first_name} {self.member_id.last_name} - {self.category_id.name} [ {self.amount} ]"

class ImgSlider(BaseClass):
    superuser_id = models.ForeignKey(SuperUserModel, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='images/')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.photo.path)
        max_size = (1000, 800)  # Change this size as needed to fit your design
        img.thumbnail(max_size)
        img.save(self.photo.path)