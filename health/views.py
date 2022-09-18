from cmath import e
from datetime import datetime
from multiprocessing import context
from unicodedata import name
from unittest import result
from django.contrib.auth.decorators import login_required
from ast import Return
from asyncio.windows_events import NULL
from cgitb import text
from django.contrib import messages
import json
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from health.decorators import is_patient
from .utilis import get_intent,symptoms,predict_disease,precautionDictionary,description, predict_diabetes
from healthApp.randgenerator import rand
from .models import Checkup, Doctor, Medicines, Profile, Usersymptoms, medicine_prescription,symptoms as Symptoms, track_medicine
import pickle
from .pedigree import Pedigree
from .Ecg import  ECG
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
import os
#from .utilis import email_check
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

#intialize ecg object

#from .models import predict_diabetes

# Create your views here.

@login_required
def chat_bot(request):
    patient = Profile.objects.get(patient=request.user)
    return render(request,'chat-bot.html',{'patient':patient})

def home(request):
    content={}
    return render(request, 'healthica/homepage.html',content)
    #return HttpResponse('<h1>hello</h1>')
@is_patient
def dashboard_patient(request,patient_id):
    patient=Profile.objects.get(p_id=patient_id)
    checkup=patient.checkups.all().order_by('-checkup_date')[:3]
    daily_prescriptions=track_medicine.objects.filter(track_for=patient,took_medicines=False,reminder_sent=True).order_by('-id')
    context={
        'patient_id':patient.p_id,
        'patient':patient,
        'checkups':checkup,
        'current_page':'home',
        'daily_pres':daily_prescriptions
    }
    return render(request,"dashboard-patient.html",context)

@login_required
def dashboard_doctor(request,doctor_id):
    doctor=Doctor.objects.get(d_id=doctor_id)
    checkups=Checkup.objects.filter(is_verified=False)
    context={
        'doctor_id':doctor_id,
        'checkups':checkups,
        'doctor':doctor,
        'current_page': 'home',
    }
    return render(request,'doctor.html',context)


def verify_checkup(request,checkup_id,patient_id):
    if request.POST:
        comments=request.POST.get('comments','None')
        vdoctor = Doctor.objects.get(doctor=request.user)
        patient = Profile.objects.get(p_id=patient_id)
        checkup = Checkup.objects.get(checkup_user=patient,checkup_id=checkup_id)
        checkup.is_verified=True
        checkup.verified_by=vdoctor
        checkup.comments=comments
        checkup.save()
    return redirect(vdoctor.dash_url())


def update_timeslots(request):
    patient=Profile.objects.get(patient=request.user)
    if request.POST:
        patient.breakfast=request.POST["breakfast"]
        patient.lunch=request.POST["lunch"]
        patient.dinner=request.POST["dinner"]
        patient.save()
        return redirect(patient.dash_url())

def update_meds(request):
     if request.POST:
        patient=Profile.objects.get(patient=request.user)
        medname=request.POST["med-name"]
        medtype=request.POST["med_type"].upper()
        dose=request.POST["dose"]
        intake=request.POST["intake"]
        slot=request.POST["slot"]
        caps=request.POST["caps_no"]
        if intake=="BEFORE FOOD":
            bf=True
            af=False
        elif intake=="AFTER FOOD":
            af = True
            bf = False
        send_time=patient.get_medicine_time(slot)
        medicine=Medicines(medicine_name=medname,medicine_type=medtype,dosage=dose,before_food=bf,after_food=af,time_slot=slot,capsules=caps)
        medicine.save()

        try:
            prescription = medicine_prescription.objects.get(
                intake_user=patient, timeslot=slot, before_food=bf, send_on=send_time)
        except medicine_prescription.DoesNotExist:
            prescription=medicine_prescription(intake_user=patient,timeslot=slot,before_food=bf,send_on=send_time)
            prescription.save()
        prescription.medicines.add(medicine)
        return redirect(patient.dash_url())
def update_reminder(request,reminder_id):
    patient = Profile.objects.get(patient=request.user)
    prescription = track_medicine.objects.get(id=reminder_id)
    prescription.took_medicines=True
    prescription.save()
    return redirect(patient.dash_url())   
def reports(request,patient_id):
    patient = Profile.objects.get(p_id=patient_id)
    checkup = patient.checkups.all()
    context = {
        'patient_id': patient.p_id,
        'patient': patient,
        'checkups': checkup,
        'current_page': 'reports'
    }
    return render(request, "reports.html", context)

def send_checkup_mail(request,checkup):
    use_https = False
    patient = Profile.objects.get(patient=request.user)
    html_tpl_path = 'email/healthica.html'
    
    context_data = {
        'patient_name': checkup.checkup_user.patient.first_name,
        'checkup_date': checkup.checkup_date,
        'checkup_type': checkup.get_checkup_type,
        'checkup_id': checkup.checkup_id,
         'patient_id': patient.p_id, 'domain': get_current_site(
        request).domain, 'protocol': 'https' if use_https else 'http'}
    email_html_template = get_template(
        html_tpl_path).render(context_data)
    receiver_email = patient.patient.email
    email_msg = EmailMessage('Checkup Report',
                             email_html_template,
                             settings.EMAIL_HOST_USER,
                             [receiver_email],
                             reply_to=[settings.EMAIL_HOST_USER]
                             )
    # this is the crucial part that sends email as html content but not as a plain text
    email_msg.content_subtype = 'html'
    email_msg.send(fail_silently=False)

def create_checkup(request,details,type):
    patient=Profile.objects.get(patient=request.user)
    details=json.dumps(details)
    chkup_id=patient.get_checkup_id()
    if type=='HEART DISEASE':
        image=request.FILES['ecg']
        checkup = Checkup(checkup_id=chkup_id, checkup_user=patient, checkup_date=datetime.now(
        ), checkup_details=details, checkup_type=type,scan_path=image)
        checkup.save()
        send_checkup_mail(request,checkup)
        return checkup
    checkup=Checkup(checkup_id=chkup_id,checkup_user=patient,checkup_date=datetime.now(),checkup_details=details,checkup_type=type)
    checkup.save()
    send_checkup_mail(request, checkup)
    return checkup

def get_response(request,intent,session):
    response=''
    print(intent)
    try:
        user_symptoms = Usersymptoms.objects.get(check_up_id=session["checkup_ID"])
    except Usersymptoms.DoesNotExist:
        user_symptoms = Usersymptoms(user=request.user,check_up_id=rand(6))
        user_symptoms.save()
    if intent == "greeting":
        response = 'Hey {}, what symptoms do you have? please enter one of your symptoms.(Ex. headache, vomiting etc.)'.format(request.user.first_name)
    elif intent == "ask_symptoms":
        try:
            main_symp=Symptoms.objects.get(symptom_name=session["message"])
            user_symptoms.my_symptoms.add(main_symp)
        except Symptoms.DoesNotExist:
            response='Please Enter correct Symptoms!'
            return response,session["checkup_ID"]
        response = "Enter one more symptom beside {}. (Enter 'No' if not)".format(session["message"])
    elif intent == "ask_symptoms-no":
        affected_symtoms=[]
        final_symptoms=[]
        for i in range(len(symptoms)):
            affected_symtoms.append(0)
        for i in range(user_symptoms.my_symptoms.count()):
            print(user_symptoms.my_symptoms.all()[1])
            affected_symtoms[symptoms.index(user_symptoms.my_symptoms.all()[i].symptom_name)]=1
            final_symptoms.append(
                user_symptoms.my_symptoms.all()[i].symptom_name)
        disease=predict_disease(affected_symtoms,final_symptoms)
        print(affected_symtoms,final_symptoms)
        response=["disease","You may have {} disease".format(disease),disease]

    elif intent == "end-chat":
        response = 'Thankyou! Take care!'
    else:
        response='Invalid Message!'
    return response,user_symptoms.check_up_id


@csrf_exempt
def predict(request):
    text = json.loads(request.body)
    msg = text["message"]
    intent=get_intent(msg)
    res,checkupid=get_response(request,intent,text)
    if(res[0]=="disease"):
        message = {"reply": res[1], "checkup_ID": checkupid}
        user_symptoms = Usersymptoms.objects.get(check_up_id=checkupid)
        details={'symptoms':[item.symptom_name for item in user_symptoms.my_symptoms.all()],'result':res[1]}
        create_checkup(request, details, 'SYMPTOMS CHECK')
    else:
        message={"reply":res,"checkup_ID":checkupid}
    return HttpResponse(json.dumps(message), content_type='application/json')



@login_required
def diabetes_view(request):
    return render(request, 'diabeticform.html',{'age':request.user.profile.age})

@login_required
def diabetes(request):
    if request.method=="POST":
        Glucoselevel=request.POST.get('Glucose Level')
        Insulin=request.POST.get('Insulin')
        bmi=request.POST.get('BMI')
        DiabetesPF=request.POST.get('Diabetes PF')
        Age=request.POST.get('Age')
        r,pred=predict_diabetes(request)#)
        details = {key:x for key, x in request.POST.items() if key != "csrfmiddlewaretoken"}
        
        if pred==1:
            result = "Chances of having Diabetes is more."
        elif int(Glucoselevel) > 200:
            result = "You maybe affected with Diabetes"
        else:
            result = "No Worries!!! You don't have Diabetes."
        details["results"]=result
        create_checkup(request, details, 'DIABETES')
        return r
        #en.save()
        #return render(request,'result.html'


@login_required
def heartdisease(request):

    #get the uploaded image
    if request.method=='POST':
        #intialize ecg object
        ecg = ECG()
        #get the uploaded image
        try:
            uploaded_file = request.FILES['ecg']
        except KeyError:
            messages.error(request,f'No file was uploaded!')
            return redirect('ecg')
        if uploaded_file is not None:
            """#### **UPLOADED IMAGE**"""
            # call the getimage method
            ecg_user_image_read = ecg.getImage(uploaded_file)
            #show the image
            

            """#### **GRAY SCALE IMAGE**"""
            #call the convert Grayscale image method
            ecg_user_gray_image_read = ecg.GrayImgae(ecg_user_image_read)
            
            
            
            """#### **DIVIDING LEADS**"""
            #call the Divide leads method
            dividing_leads=ecg.DividingLeads(ecg_user_image_read)

            
            
            """#### **PREPROCESSED LEADS**"""
            #call the preprocessed leads method
            ecg_preprocessed_leads = ecg.PreprocessingLeads(dividing_leads)

        
            
            """#### **EXTRACTING SIGNALS(1-12)**"""
            #call the sognal extraction method
            ec_signal_extraction = ecg.SignalExtraction_Scaling(dividing_leads)
            
            """#### **CONVERTING TO 1D SIGNAL**"""
            #call the combine and conver to 1D signal method
            ecg_1dsignal = ecg.CombineConvert1Dsignal()
            
                
            """#### **PERFORM DIMENSINALITY REDUCTION**"""
            #call the dimensinality reduction funciton
            ecg_final = ecg.DimensionalReduciton(ecg_1dsignal)
            
            
            """#### **PASS TO PRETRAINED ML MODEL FOR PREDICTION**"""
            #call the Pretrainsed ML model for prediction
            ecg_model=ecg.ModelLoad_predict(ecg_final)
            details={'result':ecg_model}
            create_checkup(request, details, 'HEART DISEASE')
            return render(request,'heartdisease.html',{'prediction':ecg_model})
    else:
        return render(request,'heartdisease.html')

@csrf_exempt
def updatePrescription(request):
    data=json.loads(request.body)
    pid=data["patient_id"]
    patient=Profile.objects.get(p_id=pid)
    pres = track_medicine.objects.filter(
        track_for=patient, took_medicines=False, reminder_sent=True)
    return render(request,'med-card.html',{'daily_pres':pres})
@csrf_exempt
def pedigree(request):
    data = json.loads(request.body)
    for keys,vals in data.items():
        if vals=="yes":
            data[keys]=True
        else:
            data[keys]=False
    #print(data)
    p = Pedigree(data["grandp_f"], data["grandp_m"], data["diabetic_father"], data["diabetic_mother"],
                 request.user.profile.sex.upper(), data["siblings"])
    p.get_parent_chromosomes()
    p.offsprings = p.punnet_square('disease-allele')
    p.has_diabetic_siblings()
    p.offsprings_xlinked = p.punnet_square('x-linked')
    p.determine_type_probab()
    p.x_linked_probablity()

    pedigree={"pedigree":p.probablity}
    return HttpResponse(json.dumps(pedigree), content_type='application/json')



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def show_report(request,patient_id,checkup_id):
    patient = Profile.objects.get(p_id=patient_id)
    try:
        checkup = Checkup.objects.get(
            checkup_id=checkup_id, checkup_user=patient)
    except Checkup.DoesNotExist:
        return HttpResponse('<h1>No Reports Found!</h1>')
    return render(request,'reportcard.html',{'checkup':checkup})
@login_required
def PDF(request,patient_id,checkup_id):
    patient=Profile.objects.get(p_id=patient_id)
    try:
        checkup= Checkup.objects.get(checkup_id=checkup_id,checkup_user=patient)
    except Checkup.DoesNotExist:
        return HttpResponse('<h1>No Reports Found!</h1>')
    data = {
        'patient_name':checkup.checkup_user,
        'checkup_date':checkup.checkup_date,
        'checkup_type' :checkup.checkup_type,
        'checkup_details' :json.loads(checkup.checkup_details),
        'is_verified':checkup.is_verified,
        'verified_by':checkup.verified_by,
        'checkup_id':checkup.checkup_id
    }
    

    pdf = render_to_pdf('reportpdf.html', data)
    return HttpResponse(pdf, content_type='application/pdf')
    #if pdf:
            #response = HttpResponse(pdf, content_type='application/pdf')
            #filename = "reportpdf_%s.pdf" %(data['name'])
            #content = "inline; filename='%s'" %(filename)
            #download = request.GET.get("download")
            #if download:
            #content = "attachment; filename=%s" %(filename)
            #response['Content-Disposition'] = content
            #return response
    #return HttpResponse("Not found")


 






