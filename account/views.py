from django.shortcuts import render,redirect
from django.contrib import messages
from authentication.forms import MembersForm
from authentication.models import SuperUserModel,MembersModel
# Create your views here.
def dashboard_view(request):
    return render(request, 'account/dashboard.html')

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
            
            if MembersModel.objects.get(email = email_):
                messages.warning(request,'Email Already registered!')
                return redirect('members_view')
            else:
                new_member = MembersModel(first_name=first_name_, last_name=last_name_,email = email_,mobile = mobile_,superuser_id_id = request.session['superuser_id'],is_active = is_active_)
                new_member.save()
                messages.success(request,'Member added successfully!')
                return redirect('members_view')
    context = {
        'form': form
    }
    return render(request,'account/members.html',context)

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
    return render(request,'account/forgot_password.html')


def otp_varification_view(request):
    return render(request,'account/otp_varification.html')


def profile_view(request):
    return render(request,'account/profile.html')


def logout(request):
    request.session.clear()
    messages.success(request,'Logged Out Success')
    return redirect('login_view')