from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from master.utils.ME_UNIQUE.generate_otp import generate_otp
from functools import wraps
from authentication.forms import MembersForm
from authentication.models import SuperUserModel,MembersModel

# Create your views here.

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'email' not in request.session:
            messages.warning(request, "You are not logged in yet.")
            return redirect('login_view')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@login_required
def dashboard_view(request):
    return render(request, 'account/dashboard.html')

@login_required
def members_view(request):
    form = MembersForm()
    if request.method == 'POST':
        try:
            first_name_ = request.POST.get('first_name')
            last_name_ = request.POST.get('last_name')
            email_ = request.POST.get('email')
            mobile_ = request.POST.get('mobile')
            is_active_ = request.POST.get('is_active')
        except Exception as e:
            print(e)
        else:
            if is_active_ == None:
                is_active_ = False
            else:
                is_active_ = True
            new_member = MembersModel(first_name=first_name_, last_name=last_name_,email = email_,mobile = mobile_,is_active=is_active_,superuser_id_id = request.session['superuser_id'])
            new_member.save()
            messages.success(request,'Member added successfully!')
            return redirect('members_view')

    members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    context = {
        'form': form,
        'members':members
    }
    return render(request,'account/members.html',context)

@login_required
def profile_view(request):
    return render(request,'account/profile.html')


def login_view(request):
    if request.method == "POST":
        email_ = request.POST['email']
        password_ = request.POST['password']
        try:
            getsuperuser = SuperUserModel.objects.get(email = email_)
        except SuperUserModel.DoesNotExist:
            messages.info(request,'User Does Not Exists')
            redirect('login_view')
        else:
            if getsuperuser:
                if getsuperuser.password == password_:
                    request.session['superuser_id'] = getsuperuser.id
                    request.session['email'] = getsuperuser.email
                    request.session['first_name'] = getsuperuser.first_name
                    request.session['last_name'] = getsuperuser.last_name
                    request.session['mobile'] = getsuperuser.mobile
                    messages.success(request,'Login Success')
                    return redirect('dashboard_view')
                else:
                    messages.warning(request,'Email and Password does not match')
                    return redirect('login_view')
            else:
                messages.info(request,'User Not Exist')
                return redirect('login_view')
    if 'email' in request.session:
        return redirect('dashboard_view')
    return render(request,'account/login.html')


def forgot_password_view(request):
    if request.method == "POST":
        email_ = request.POST['email']
        
        try:
            getsuperuser = SuperUserModel.objects.get(email = email_)

        except SuperUserModel.DoesNotExist:
            messages.warning(request,'Email Not Registered Yet!')
            return redirect('login_view')

        else:
            if getsuperuser:
                otp_ = generate_otp()
                getsuperuser.otp = otp_
                getsuperuser.save()
                subject = 'Forgot Password OTP'
                message = f"""
                Dear {getsuperuser.first_name} {getsuperuser.last_name},

                You have requested to reset your password. Please use the following One Time Password (OTP) to proceed:

                OTP: {otp_}

                If you did not request this password reset, please ignore this email.

                Thank you,
                Miscellaneous expenses Team                
                """
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [f'{email_}']
                send_mail(subject,message,from_email,recipient_list)
                messages.info(request,f"Password Reset Otp Sent on {email_} successfully!")
                context = {
                    "email" : email_
                }
                return render(request,'account/otp_varification.html',context)
    return render(request,'account/forgot_password.html')

def otp_varification_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']
        password_ = request.POST['password']
        confirm_password_ =  request.POST['confirm_password']
        try:
            getsuperuser = SuperUserModel.objects.get(email = email_ )
        except SuperUserModel.DoesNotExist:
            messages.warning(request,'User Not Exist')
            return redirect('login_view')
        else:
            if getsuperuser:
                if otp_ == getsuperuser.otp:
                    if password_ == confirm_password_:
                        getsuperuser.password = password_
                        getsuperuser.save()
                        messages.success(request,'Password Changed')
                        return redirect('login_view')
                    else:
                        messages.warning(request,'Password and Confirm Password does not match!')
                        context = {
                            'email': email_
                        }
                        return render(request,'account/otp_varification.html',context)
                else:
                    
                    otp_ = generate_otp()
                    getsuperuser.otp = otp_
                    getsuperuser.save()
                    subject = 'Forgot Password OTP'
                    message = f"""
                    Dear {getsuperuser.first_name} {getsuperuser.last_name},

                    You have requested to reset your password. Please use the following One Time Password (OTP) to proceed:

                    OTP: {otp_}

                    If you did not request this password reset, please ignore this email.

                    Thank you,
                    Miscellaneous expenses Team                
                    """
                    messages.warning(request,f"Password Reset Otp again Sent on {email_} successfully!")
                    from_email = settings.EMAIL_HOST_USER
                    recipient_list = [f'{email_}']
                    send_mail(subject,message,from_email,recipient_list)
                    context = {
                        "email" : email_
                    }
                    return render(request,'account/otp_varification.html',context)

    return render(request,'account/otp_varification.html')

@login_required
def logout(request):
    request.session.clear()
    messages.success(request,'Logged Out Success')
    return redirect('login_view')



def members_login_view(request):
    if request.method == "POST":
        email_ = request.POST['email']
        password_ = request.POST['password']
        
        try:
            getMembers = MembersModel.objects.get(email = email_)
        except MembersModel.DoesNotExist:
            messages.warning(request,"Member Does not Exist!")
            redirect('members_login_view')
        else:
            if password_ == getMembers.password:
                request.session['superuser_id'] = getMembers.superuser_id_id
                request.session['members_id'] = getMembers.id
                request.session['first_name'] = getMembers.first_name
                request.session['last_name'] = getMembers.last_name
                request.session['email'] = getMembers.email
                request.session['mobile'] = getMembers.mobile
                messages.success(request,'Login Success!')
                return redirect('members_dashboard_view')
    return render(request,'account/members_login.html')


def members_dashboard_view(request):
    return render(request,'account/members_dashboard.html')

def members_profile_view(request):
    return render(request,'account/members_profile.html')