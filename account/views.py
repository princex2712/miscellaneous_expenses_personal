from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail

from master.utils.ME_DATETIME.me_time import DateTimeInformation
from master.utils.ME_UNIQUE.generate_otp import generate_otp
from functools import wraps
from authentication.forms import MembersForm
from authentication.models import MembersModel,SuperUserModel
from .models import IncomeModel

# Create your views here.
datetimeinfo = DateTimeInformation()

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
    context = {
        'start_date_of_month':datetimeinfo.get_startdate_of_month,
        'current_date_of_month':datetimeinfo.get_current_date,
    }
    return render(request,'account/profile.html',context)


def login_view(request):
    if request.method == "POST":
        email_ = request.POST['email']
        password_ = request.POST['password']
        try:
            getmemberuser = SuperUserModel.objects.get(email = email_)
        except SuperUserModel.DoesNotExist:
            messages.info(request,'User Does Not Exists')
            redirect('login_view')
        else:
            if getmemberuser:
                if getmemberuser.password == password_:
                    request.session['superuser_id'] = getmemberuser.id
                    request.session['email'] = getmemberuser.email
                    request.session['first_name'] = getmemberuser.first_name
                    request.session['last_name'] = getmemberuser.last_name
                    request.session['mobile'] = getmemberuser.mobile
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
            getmemberuser = MembersModel.objects.get(email=email_)
        except MembersModel.DoesNotExist:
            messages.info(request,'User Does Not Exists')
            redirect('login_view')

        otp_ = generate_otp()

        getmemberuser.otp = otp_
        getmemberuser.save()

        subject = 'Forgot Password OTP'
        message = f"""
        Dear {getmemberuser.first_name} {getmemberuser.last_name},

        You have requested to reset your password. Please use the following One Time Password (OTP) to proceed:

        OTP: {otp_}

        If you did not request this password reset, please ignore this email.

        Thank you,
        Miscellaneous expenses Team                
        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email_]
        send_mail(subject, message, from_email, recipient_list)

        messages.info(request, f"Password Reset OTP sent to {email_} successfully!")
        context = {
            "email": email_
        }
        return render(request, 'account/otp_varification.html', context)

    return render(request, 'account/forgot_password.html')

def otp_varification_view(request):
    if request.method == 'POST':
        email_ = request.POST['email']
        otp_ = request.POST['otp']
        password_ = request.POST['password']
        confirm_password_ = request.POST['confirm_password']

        try:
            user = MembersModel.objects.get(email=email_)
        except MembersModel.DoesNotExist:
            messages.info(request,'User Does Not Exists')
            redirect('login_view')

        if user:
            if otp_ == user.otp:
                if password_ == confirm_password_:
                    user.password = password_
                    user.save()
                    messages.success(request, 'Password Changed Successfully')
                    return redirect('login_view')
                else:
                    messages.warning(request, 'Password and Confirm Password do not match!')
            else:
                new_otp = generate_otp()
                user.otp = new_otp
                user.save()

                subject = 'Forgot Password OTP'
                message = f"""
                Dear {user.first_name} {user.last_name},

                You have requested to reset your password. Please use the following One Time Password (OTP) to proceed:

                OTP: {new_otp}

                If you did not request this password reset, please ignore this email.

                Thank you,
                Miscellaneous expenses Team                
                """
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email_]
                send_mail(subject, message, from_email, recipient_list)

                messages.warning(request, f"New OTP sent to {email_} successfully!")

        else:
            messages.warning(request, 'User does not exist')
            return redirect('login_view')

    context = {'email': email_}
    return render(request, 'account/otp_varification.html', context)

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
            if getMembers.is_active != False:
                if password_ == getMembers.password:
                    request.session['superuser_id'] = getMembers.superuser_id_id
                    request.session['members_id'] = getMembers.id
                    request.session['first_name'] = getMembers.first_name
                    request.session['last_name'] = getMembers.last_name
                    request.session['email'] = getMembers.email
                    request.session['mobile'] = getMembers.mobile
                    messages.success(request,'Login Success!')
                    return redirect('members_dashboard_view')
                else:
                    messages.warning(request,"Invalid Password or email!")
                    return redirect('members_login_view')
            else:
                messages.warning(request,"Account is deactive Contact Your Admin!")
                return redirect('members_login_view')
    return render(request,'account/members_login.html')

@login_required
def members_dashboard_view(request):
    return render(request,'account/members_dashboard.html')

@login_required
def members_profile_view(request):
    context = {
        'start_date_of_month':datetimeinfo.get_startdate_of_month,
        'current_date_of_month':datetimeinfo.get_current_date,
    }
    return render(request,'account/members_profile.html',context)

@login_required
def update_member_view(request,id):
    getUser = MembersModel.objects.get(id=id)
    context = {
        'member':getUser
    }
    if request.method=="POST":
        getUser.first_name = request.POST['first_name']
        getUser.last_name = request.POST['last_name']
        getUser.email = request.POST['email']
        getUser.mobile = request.POST['mobile']
        
        if request.POST.get('is_active') == 'on':
            is_active_ = True
        else:
            is_active_ = False

        getUser.is_active = is_active_
        getUser.save()
        messages.success(request,f"{getUser.first_name} {getUser.last_name} is Updated Successfully")
        return redirect('members_view')

    return render(request,'account/update_member.html',context)

@login_required
def delete_member_view(request,id):
    getUser = MembersModel.objects.get(id=id)
    messages.success(request,f"{getUser.first_name} {getUser.last_name} Deleted Successfully")
    getUser.delete()
    return redirect("members_view")

@login_required
def income_view(request):  

    if request.method == "POST":
        member_id_ = request.POST['member']
        date_ = request.POST['date']
        amount_ = request.POST['income_amount']

        add_income=IncomeModel.objects.create(
            member_id_id=member_id_,
              amount=amount_,
                date=date_)
        add_income.save()
        return redirect('income_view')
    
    members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    context={
        'members':members
    }
    return render(request,'account/income.html',context)

@login_required
def members_income_view(request):
    if request.method == "POST":
        member_id_ = request.POST['member']
        date_ = request.POST['date']
        amount_ = request.POST['income_amount']

        add_income=IncomeModel.objects.create(
            member_id_id=member_id_,
                amount=amount_,
                date=date_)
        add_income.save()
        return redirect('members_income_view')
    
    members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    context={
        'members':members
    }
    return render(request,'account/members_income.html',context)