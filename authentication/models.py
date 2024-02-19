from django.db import models
from master.models import BaseClass
from django.core.mail import send_mail

from master.utils.ME_UNIQUE.generate_password import generate_password
from project import settings

class SuperUserModel(BaseClass):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    mobile = models.CharField(max_length=255)
    password = models.CharField(max_length=255,blank=True)
    is_active = models.BooleanField(default=True)
    otp = models.CharField(max_length=50,default=100000)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = generate_password(8)
            subject = 'Login Credential Fro Miscellaneous Expense'
            message = f'Hello {self.first_name} {self.last_name},\n\n' \
                      f'We are pleased to inform you that your login credentials have been successfully created:\n\n' \
                      f'Email: {self.email}\n' \
                      f'Password: {self.password}\n\n' \
                      f'If you have any questions or concerns, feel free to reach out to us.\n\n' \
                      f'Thank you,\n' \
                      f'[Miscellaneous Expense] Team'
            from_mail = settings.EMAIL_HOST_USER
            to_mail = [f'{self.email}']
            send_mail(subject,message,from_mail,to_mail)
            
        super(SuperUserModel,self).save(*args, **kwargs)
        if not MembersModel.objects.filter(superuser_id=self).exists():
                members_model_instance = MembersModel(
                    superuser_id=self,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    email=self.email,
                    mobile=self.mobile,
                    password=self.password,
                    is_active=self.is_active,
                    is_super_user=True
                )
                members_model_instance.save()
        else:
            super().save(*args, **kwargs)

class MembersModel(BaseClass):
    superuser_id = models.ForeignKey(SuperUserModel, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255,blank=True)
    mobile = models.CharField(max_length=255)
    password = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_super_user = models.BooleanField(default=False)
    otp = models.CharField(max_length=50,default=100000)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = generate_password(8)

        super(MembersModel, self).save(*args, **kwargs)
