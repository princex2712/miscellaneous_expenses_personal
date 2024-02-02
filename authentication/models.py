from django.db import models
from master.models import BaseClass

from master.utils.ME_UNIQUE.generate_password import generate_password

class SuperUserModel(BaseClass):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=255)
    password = models.CharField(max_length=255,blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = generate_password(8)
            
        return super().save(*args, **kwargs)


