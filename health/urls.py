from unicodedata import name
from django.urls import path
from . import views

#from .utilis import update_symptoms

urlpatterns = [
    path('chat-bot', views.chat_bot, name='chat_bot'),
    path('predict', views.predict, name='predict'),
    path('home',views.home,name='home'),
    path('<str:patient_id>/dashboard/PT',views.dashboard_patient,name='patient-dash'),
    path('<str:patient_id>/dashboard/PT/reports',views.reports, name='patient-reports'),
    path('diabetes-predict', views.diabetes_view, name='diabetes-predict'),
    path('diabetes-result', views.diabetes, name='predicteddiabetes'),
    path('pedigree',views.pedigree,name="pedigree"),
    path('updatePrescription', views.updatePrescription, name="updatePrescription"),
    path('heart-disease',views.heartdisease, name='ecg'),
    path('testpdf',views.PDF,name="test"),
    path('<str:patient_id>/reports/<str:checkup_id>',views.PDF, name='pdfcheckup'),
    path('<str:patient_id>/myreport/<str:checkup_id>',views.show_report, name='patient-report'),
    path('timesave',views.update_timeslots,name="timesave"),
    path('updatemedicine',views.update_meds,name="medicine-update"),
    path('update-remainder/<int:reminder_id>', views.update_reminder, name="reminder-update"),
    #path('save-symp',update_symptoms,name='symptoms-update'),
    #Doctor Links
    path('<str:doctor_id>/dashboard/DR',views.dashboard_doctor, name='doctor-dash'),
    path('verify/<str:patient_id>/<str:checkup_id>',views.verify_checkup,name='verify-checkup')
]

