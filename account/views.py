from django.shortcuts import render
from authentication.forms import MembersForm
# Create your views here.
def dashboard_view(request):
    return render(request, 'account/dashboard.html')

def members_view(request):
    form = MembersForm()
    context = {
        'form': form
    }
    return render(request,'account/members.html',context)

def profile_view(request):
    return render(request,'account/profile.html')