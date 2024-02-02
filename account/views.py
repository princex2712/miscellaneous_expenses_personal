from django.shortcuts import render

# Create your views here.
def dashboard_view(request):
    return render(request, 'account/dashboard.html')

def members_view(request):
    return render(request,'account/members.html')

def profile_view(request):
    return render(request,'account/profile.html')