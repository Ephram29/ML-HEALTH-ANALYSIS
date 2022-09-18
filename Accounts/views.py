from ast import Return
from multiprocessing import context
from pydoc import Doc
from xmlrpc.client import DateTime
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm 
from .forms import CreateUserForm
from django.http import HttpResponse,Http404
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from health.forms import Patientform,Doctorform
from .utils import get_IDs
from health.models import Profile,Doctor
from datetime import datetime
from .decorators import not_loggedin
# Create your views here.

@not_loggedin
def FormRender(request):
    #print(request.body)
    context={}
    form=CreateUserForm()
    if request.POST:
        form=CreateUserForm(request.POST)
        
    context={'form': form}
    return render(request,'login.html',context)

def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user=form.save()
            print("test1")
            login(request, user)
            messages.info(request,f"Please Complete your Registration.")
            return redirect('registration')
        else:
            return FormRender(request)
    return Http404()


def loginpage(request):
    if request.POST:
        user_name=request.POST["username"]
        pass_word=request.POST["password"]
        user=authenticate(request,username=user_name,password=pass_word)
        if user is not None:
            login(request,user)
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            messages.success(request,f'logged in as {user_name}')
            return redirect('home')
        else:
            messages.error(request,f"Invalid Credentials")
            return redirect('login-register')
    return Http404()




def user_logout(request):
    context={} 
    logout(request)
    messages.success(request,f"Logout successfull")
    return redirect('home')


#@not_loggedin
def form_view(request):
    context={}
    while True:
        D_id,P_id=get_IDs()
        doctor=None
        patient=None
        try:
            doctor = Doctor.objects.get(d_id=D_id)
            patient= Profile.objects.get(p_id=P_id)
        except (Doctor.DoesNotExist,Profile.DoesNotExist):
            pass
        if doctor==None and patient==None:
            break
    initia_dataD={'d_id':D_id}
    initia_dataP = {'p_id': P_id}
    context = {'pform': Patientform(
        initial=initia_dataP), 'dform': Doctorform(initial=initia_dataD)}
    return render(request,'pseudo-form.html',context)



def Doctorregister(request):
    if request.method == 'POST':
        print(request.POST)
        D_id=request.POST.get("doctor_id",False)
        try:
            doctor = Doctor.objects.get(d_id=D_id,doctor=request.user)
        except Doctor.DoesNotExist:
            doctor = Doctor(doctor=request.user, d_id=D_id)
            doctor.save()
        form = Doctorform(request.POST,instance=doctor)
        if form.is_valid():
            user=form.save()
            messages.success(request, f"Registered Successfully as Doctor.")
            return redirect('home')
        else:
            return HttpResponse(form.errors.as_data())
     



def Patientregister(request):
    
    if request.method == 'POST':
        P_id = request.POST.get("p_id", False)
        patient=Profile(patient=request.user,p_id=P_id)
        form = Patientform(request.POST,instance=patient)
        if form.is_valid():
            user=form.save()
            print("test1")
            today = datetime.today()
            user.age = int(today.year-user.dob.year)
            print("age=",user.age)
            user.save()
            messages.success(request,f"Registered Successfully as Patient.")
            return redirect('home')
        else:
            return FormRender(request)
    return Http404()



