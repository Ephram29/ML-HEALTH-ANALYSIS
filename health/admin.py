from django.contrib import admin
from .models import Checkup, Medicines, medicine_prescription, symptoms,Usersymptoms,Doctor,Profile, track_medicine
# Register your models here.

class med_pread(admin.ModelAdmin):
    list_display=('pk','intake_user','send_on','timeslot')
class track_medad(admin.ModelAdmin):
    list_display=('pk','prescription','medicine_date')
class symptomsad(admin.ModelAdmin):
    list_display = ('pk','symptom_name')

class usersymp_ad(admin.ModelAdmin):
    list_display=('pk','check_up_id','user')


class doctor_ad(admin.ModelAdmin):
    list_display = ('pk', 'd_id', 'doctor')


class patient_ad(admin.ModelAdmin):
    list_display = ('pk', 'p_id', 'patient')
class checkup_ad(admin.ModelAdmin):
    list_display=('pk','checkup_id','checkup_user')

admin.site.register(Checkup,checkup_ad)
admin.site.register(Doctor,doctor_ad)
admin.site.register(symptoms,symptomsad)
admin.site.register(Usersymptoms,usersymp_ad)
admin.site.register(Profile,patient_ad)
admin.site.register(Medicines)
admin.site.register(medicine_prescription,med_pread)
admin.site.register(track_medicine,track_medad)
