from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

import openpyxl

from master.utils.ME_DATETIME.me_time import DateTimeInformation
from master.utils.ME_UNIQUE.generate_otp import generate_otp
from master.utils.ME_REPORT.me_report import IncomeExpense
from master.utils.ME_FORMAT.format_amount import format_amount
from functools import wraps
from authentication.forms import MembersForm
from authentication.models import MembersModel
from .models import IncomeModel,Category,Expenses

# creating object to use classes 
datetimeinfo = DateTimeInformation()
start_date_of_month=datetimeinfo.get_startdate_of_month()
current_date_of_month=datetimeinfo.get_current_date()

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
    user = MembersModel.objects.get(email = request.session['email'])
    unique_category_names = Category.objects.filter(expenses__superuser_id=request.session['superuser_id']).values_list('id','name').distinct()
    context = {
        'user':user,
        'unique_category_names':unique_category_names
    }
    return render(request, 'account/dashboard.html',context)

@login_required
def get_record_via_filter(request,category_id):
    getmember = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    ExpensesRecord = []
    for member in getmember:
        getExpense = Expenses.objects.filter(member_id_id=member.id).filter(category_id_id = category_id).filter(date__range=[datetimeinfo.convert_date_format(start_date_of_month),datetimeinfo.convert_date_format(current_date_of_month)])
        if getExpense.exists():
            ExpensesRecord.append(getExpense)
            print(getExpense)
    return redirect('dashboard_view')
@login_required
def members_view(request):
    user = MembersModel.objects.get(email = request.session['email'])
    form = MembersForm()
    if request.method == 'POST':
        try:
            first_name_ = request.POST.get('first_name')
            last_name_ = request.POST.get('last_name')
            email_ = request.POST.get('email')
            mobile_ = request.POST.get('mobile')
            is_active_ = request.POST.get('is_active')
            if MembersModel.objects.filter(email=email_).exists():
                messages.warning(request,'Email Already Taken!')
                return redirect('members_view')
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
        'members':members,
        'user':user
    }
    return render(request,'account/members.html',context)

@login_required
def profile_view(request):
    getmembers = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    user = MembersModel.objects.get(email=request.session['email'])
    total_income = 0
    total_expense = 0
    for member in getmembers:
        get_income = IncomeModel.objects.filter(member_id_id=member.id).filter(
            date__range=[
                datetimeinfo.convert_date_format(start_date_of_month),
                datetimeinfo.convert_date_format(current_date_of_month)
                ])
        total_amount = get_income.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_income += total_amount

        get_expense = Expenses.objects.filter(member_id_id=member.id).filter(
            date__range=[
                datetimeinfo.convert_date_format(start_date_of_month),
                datetimeinfo.convert_date_format(current_date_of_month)
                ])
        total_amount = get_expense.aggregate(total_amount=Sum('amount'))['total_amount'] or 0
        total_expense += total_amount
    remaining_amount = total_income - total_expense
    context = {
        'start_date_of_month':start_date_of_month,
        'current_date_of_month':current_date_of_month,
        'total_income':format_amount(total_income),
        'user':user,
        'total_expense':format_amount(total_expense),
        'remaining_amount':format_amount(remaining_amount)
    }
    return render(request,'account/profile.html',context)


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

def login_view(request):
    if request.method == "POST":
        email_ = request.POST['email']
        password_ = request.POST['password']
        
        try:
            getMembers = MembersModel.objects.get(email = email_)
        except MembersModel.DoesNotExist:
            messages.warning(request,"Member Does not Exist!")
            redirect('login_view')
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
                    return redirect('dashboard_view')
                else:
                    messages.warning(request,"Invalid Password or email!")
                    return redirect('login_view')
            else:
                messages.warning(request,"Account is deactive Contact Your Admin!")
                return redirect('login_view')
    return render(request,'account/login.html')

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
    user = MembersModel.objects.get(email = request.session['email'])
    if request.method == "POST":
        member_id_ = request.POST['member']
        date_ = request.POST['date']
        amount_ = request.POST['income_amount']

        add_income=IncomeModel.objects.create(
            superuser_id_id=request.session['superuser_id'],
            member_id_id=member_id_,
              amount=amount_,
                date=date_)
        add_income.save()
        return redirect('income_view')
    
    members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    get_income= IncomeModel.objects.filter(superuser_id_id=request.session['superuser_id']).filter(date__range=[datetimeinfo.convert_date_format(start_date_of_month),datetimeinfo.convert_date_format(current_date_of_month)])
    context={
        'members':members,
        'get_income':get_income,
        'user':user,
        'start_date_of_month':datetimeinfo.convert_date_format(start_date_of_month),
        'current_date_of_month':datetimeinfo.convert_date_format(current_date_of_month)
    }
    return render(request,'account/income.html',context)

def income_date_filter(request):
    if request.method == "POST":
        get_income = IncomeModel.objects.filter(superuser_id_id=request.session['superuser_id'])
        members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
        user = MembersModel.objects.get(email=request.session['email'])
        context = {
            'user': user,
            'members': members,
        }

        if 'date_chk_box' in request.POST:
            try:
                startdate = request.POST['startdate']
                enddate = request.POST['enddate']
                get_income = get_income.filter(date__range=[startdate, enddate])
                context['start_date_of_month'] = startdate
                context['current_date_of_month'] = enddate
                context['get_income'] = get_income
            except Exception as e:
                print(e)
                messages.warning(request,"Invalid or Empty Date!")
                return redirect('income_view')
            
        if 'member_chk_box' in request.POST:
            try:
                member = request.POST['member']
                get_income = get_income.filter(member_id_id = member)
                context['get_income'] = get_income
            except Exception as e:
                print(e)
                messages.warning(request,"Invalid or Empty Member!")
                return redirect('income_view')

        return render(request, 'account/income.html', context)
    else:
        return redirect("Invalid request method")

@login_required
def expenses_view(request):
    user = MembersModel.objects.get(email = request.session['email'])
    categories = Category.objects.all()
    members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    get_expenses = Expenses.objects.filter(superuser_id_id=request.session['superuser_id']).filter(date__range=[datetimeinfo.convert_date_format(start_date_of_month),datetimeinfo.convert_date_format(current_date_of_month)])
    if request.method=='POST':
        try:
            date_ = request.POST['date']
            amount_ = request.POST['income_amount']
            description_ = request.POST['description']
            member_id=request.POST['member']
            category_id=request.POST['category']
            superuser_id_=request.session['superuser_id']
            new_expense = Expenses(superuser_id_id=superuser_id_,date=date_,amount=amount_,description=description_,member_id_id=member_id,category_id_id=category_id)
            new_expense.save()
            return redirect('expenses_view')
        except Exception as e:
            return redirect('profile_view')
    context = {
        'user':user,
        'categories':categories,
        'get_expenses':get_expenses,
        'members':members,
        'start_date_of_month':datetimeinfo.convert_date_format(start_date_of_month),
        'current_date_of_month':datetimeinfo.convert_date_format(current_date_of_month)
    }
    return render(request, 'account/expense.html',context)

def expense_date_filter(request):
    if request.method == "POST":
        get_expenses = Expenses.objects.filter(superuser_id_id=request.session['superuser_id'])
        user = MembersModel.objects.get(email=request.session['email'])
        categories = Category.objects.all()
        members = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
        context = {
            'user': user,
            'members': members,
            'categories': categories,
        }
        if 'date_chk_box' in request.POST:
            try:
                startdate = request.POST['startdate']
                enddate = request.POST['enddate']
                get_expenses = get_expenses.filter(date__range=[startdate, enddate])
                context['start_date_of_month'] = startdate
                context['current_date_of_month'] = enddate
                context['get_expenses'] = get_expenses
            except Exception as e:
                print(e)
                messages.warning(request,"Invalid or Empty Date!")
                return redirect('expenses_view')
        
        if 'category_chk_box' in request.POST:
            try:
                category = request.POST['category']
                get_expenses = get_expenses.filter(category_id_id=category)
                context['get_expenses'] = get_expenses
            except:
                print(e)
                messages.warning(request,"Invalid or Empty Category!")
                return redirect('expenses_view')

        if 'member_chk_box' in request.POST:
            try:
                member = request.POST['member']
                get_expenses = get_expenses.filter(member_id_id = member)
                context['get_expenses'] = get_expenses
            except Exception as e:
                print(e)
                messages.warning(request,"Invalid or Empty Member!")
                return redirect('expenses_view')   
            
        return render(request, 'account/expense.html', context)
    else:
        return redirect("Invalid request method")

def update_income_view(request,id):
    getIncome = IncomeModel.objects.get(id=id)
    getmember = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    user = MembersModel.objects.get(email = request.session['email'])
    if request.method=="POST":
        getIncome.date = request.POST['date']
        getIncome.amount = request.POST['income_amount']
        getIncome.member_id_id = request.POST['member']
        getIncome.save()
        messages.success(request,"Income Update Successfully!")
        return redirect('income_view')
    context = {
        'income':getIncome,
        'user':user,
        'members':getmember
    }
    return render(request,'account/update_income.html',context)

def delete_income_view(request,id):
    getIncome = IncomeModel.objects.get(id=id)
    getIncome.delete()
    messages.success(request,"Income Deleted Successfully!")
    return redirect('income_view')

def update_expense_view(request,id):
    getexpense = Expenses.objects.get(id=id)
    getmember = MembersModel.objects.filter(superuser_id_id=request.session['superuser_id'])
    categories = Category.objects.all()
    
    if request.method == "POST":
        getexpense.member_id_id = request.POST['member']
        getexpense.category_id_id = request.POST['category']
        getexpense.date = request.POST['date']
        getexpense.amount = request.POST['expense_amount']
        getexpense.description = request.POST['description']
        getexpense.save()
        messages.success(request,"Expense Update Successfully!")
        return redirect('income_view')
    context = {
        'getexpense':getexpense,
        'members':getmember,
        'categories':categories
    }
    return render(request,'account/update_expense.html',context)

def delete_expense_view(request, id):
    try:
        getexpense = Expenses.objects.get(id=id)
        getexpense.delete()
        messages.success(request, "Expense Deleted Successfully!")
    except Expenses.DoesNotExist:
        messages.error(request, "Expense does not exist!")
    
    return redirect('expenses_view')


def download_income_report(request):
    ie = IncomeExpense(request.session['superuser_id'])
    member_income_list = []
    total_income = ie.current_total_income()
    for member in ie.getmember:
        member_income = IncomeModel.objects.filter(member_id_id=member.id).filter(date__range=[datetimeinfo.convert_date_format(start_date_of_month),datetimeinfo.convert_date_format(current_date_of_month)])
        if member_income.exists():
            member_income_list.append({'incomes':member_income})
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Income Report'

    # Headers
    worksheet.append(['Member Name', 'Income Date', 'Total Income'])

    # Data rows
    for record in member_income_list:
        incomes_queryset = record['incomes']
        for income_instance in incomes_queryset:
            worksheet.append([income_instance.member_id.first_name + ' ' + income_instance.member_id.last_name, income_instance.date,  income_instance.amount])

    worksheet.append(['Total', '', total_income])

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=income_report.xlsx'

    # Save workbook to response
    workbook.save(response)

    return response

def download_expense_report(request):
    ie = IncomeExpense(request.session['superuser_id'])
    total_expense = ie.current_total_expense()
    member_expense_list = []
    for member in ie.getmember:
        member_expense = Expenses.objects.filter(member_id_id=member.id).filter(date__range=[datetimeinfo.convert_date_format(start_date_of_month),datetimeinfo.convert_date_format(current_date_of_month)])
        if member_expense.exists():
            member_expense_list.append({'expenses':member_expense})
    
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Expense Report'

    # Headers
    worksheet.append(['Member Name', 'Expense Date', 'Category' , 'Expense'])

    # Data rows
    for record in member_expense_list:
        incomes_queryset = record['expenses']
        for expense_instance in incomes_queryset:
            worksheet.append([expense_instance.member_id.first_name + ' ' + expense_instance.member_id.last_name, expense_instance.date,expense_instance.category_id.name,expense_instance.amount])

    worksheet.append(['Total', '','', total_expense])

    # Create response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=expense_report.xlsx'

    # Save workbook to response
    workbook.save(response)

    return response
    
    


