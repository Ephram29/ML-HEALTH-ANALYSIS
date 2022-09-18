from ctypes.wintypes import MSG
from datetime import datetime, timedelta
from distutils.command import upload
from email import message
from math import remainder
from sys import maxsize
from time import sleep
from urllib import request
from xml.parsers.expat import model
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import MINUTES, PeriodicTask, CrontabSchedule, PeriodicTasks
from django.urls import reverse
import json
# Create your models here.
class Profile(models.Model):
    patient=models.OneToOneField(User,on_delete=models.CASCADE)
    p_id=models.CharField(max_length=12,null=True)
    username = models.CharField(max_length=12, null=True)
    email = models.EmailField(max_length=40, null=True)
    phone = models.PositiveBigIntegerField(null=True)
    fname = models.CharField(max_length=20, null=True)
    lname = models.CharField(max_length=20, null=True)
    age = models.IntegerField(null=True)
    sex=models.CharField(max_length=10)
    dob=models.DateField(default=datetime.today)
    height = models.FloatField( null=True)
    weight = models.FloatField( null=True)
    breakfast = models.TimeField(null=True)
    lunch = models.TimeField(null=True)
    dinner = models.TimeField(null=True)
    blood_grp = models.CharField(max_length=10, null=True)

    def __str__(self):
        return self.patient.username
    def dash_url(self):
        return reverse('patient-dash', kwargs={'patient_id': self.p_id})
    def bmi(self):
        BMI = self.weight / (self.height/100)**2
        return round(BMI,2)
    def get_medicine_time(self,slot):
        if slot=="BREAK FAST":
            return self.breakfast
        elif slot=="LUNCH":
            return self.lunch
        elif slot=="DINNER":
            return self.dinner
    #checkup id genration
    def get_checkup_id(self):
        checkup=self.checkups.all()
        checkup_count=checkup.count()
        checkup_id='CHKUP'+str(checkup_count)
        return checkup_id
    def time_exists(self):
        if self.breakfast or self.lunch or self.dinner:
            return True
#class Doctor(models.Model):
#class Checkup
#class disease
#class mental_health


class Doctor(models.Model):
    doctor = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone = models.PositiveBigIntegerField(null=True)
    specialization = models.CharField(max_length=30, null=True)
    d_id = models.CharField(max_length=12, null=True)
    works_in = models.CharField(max_length=50, null=True)
    sex = models.CharField(max_length=12, null=True)

    def __str__(self):
        if self.doctor is not None:
            return self.doctor.username
        return 'None'

    def dash_url(self):
        return reverse('doctor-dash', kwargs={'doctor_id': self.d_id})

class Medicines(models.Model):
    timeslots=(('BREAK FAST',1),
                    ('LUNCH',2),
                    ('DINNER',3)
              )
    med_type=(('PILLS','PILLS'),
              ('TABLET','TABLET'),
              ('SYRINGE','SYRINGE'),
              ('SYRUP','SYRUP'))
    medicine_name = models.CharField(max_length=100)
    medicine_type=models.CharField(max_length=30,choices=med_type,default='PILLS')
    dosage=models.FloatField(default=0)
    before_food=models.BooleanField(default=True)
    after_food=models.BooleanField(default= False)
    capsules = models.IntegerField(null=True)
    time_slot = models.CharField(choices=timeslots, max_length=20)
    
    def med_unit(self):
        if self.medicine_type in ["TABLET","PILLS"]:
            return str(self.dosage)+"mg, "+str(self.capsules)+" capsules"
        else:
            return str(self.dosage)+"ml"

class medicine_prescription(models.Model):
    timeslots = (('BREAK FAST', 1),
                 ('LUNCH', 2),
                 ('DINNER', 3)
                 )
    intake_user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    medicines = models.ManyToManyField(Medicines)
    timeslot = models.CharField(choices=timeslots, default=1, max_length=20)
    before_food = models.BooleanField(default=True)
    send_on=models.TimeField()
    message = models.TextField(max_length=200, default='Its Time to take your medicine')
    def med_time(self):
        if self.before_food:
            string="Before "
        else:
            string="After "
        return string+self.timeslot.lower().capitalize()
    def med_class(self):
        cls=""
        if self.timeslot=="BREAK FAST":
            cls="badge-warning"
        elif self.timeslot=="LUNCH":
            cls="badge-success"
        elif self.timeslot=="DINNER":
            cls="badge-dark"
        if self.before_food and self.timeslot == "DINNER":
            cls="badge-grey"
        elif self.before_food:
            cls+="-light"
        return cls


@receiver(post_save, sender=medicine_prescription)
def notification_handler(sender, instance, created, **kwargs):
    # call group_send function directly to send notificatoions or you can create a dynamic task in celery beat
    if created:
        if instance.before_food:
            send_time = datetime.combine(datetime.today(),instance.send_on) - timedelta(minutes=30)
            name=f"medicine-notification-{instance.intake_user.p_id}-{instance.timeslot}-BF"
        else:
            send_time = datetime.combine(datetime.today(),instance.send_on) + timedelta(minutes=30)
            name = f"medicine-notification-{instance.intake_user.p_id}-{instance.timeslot}-AF"

        schedule, created = CrontabSchedule.objects.get_or_create(hour=send_time.hour, minute=send_time.minute)
        task = PeriodicTask.objects.create(crontab=schedule, name=name, task="notifications.tasks.medicine_notification", args=json.dumps((instance.id,)))


class track_medicine(models.Model):
    prescription = models.ForeignKey(medicine_prescription, on_delete=models.CASCADE, related_name="track_medicine")
    track_for=models.ForeignKey(Profile,on_delete=models.CASCADE,null=True)
    medicine_date=models.DateField()
    took_medicines = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    class meta:
        ordering=('-medicine_date')
    def get_url(self):
        return reverse('reminder-update', kwargs={'reminder_id': self.id})
class Trackweight(models.Model):
    current_weight=models.FloatField()
    user=models.ForeignKey(Profile,on_delete=models.CASCADE)
    timestamp=models.DateTimeField()


class symptoms(models.Model):
    symptom_name=models.CharField(max_length=100,null=False)
    symptom_desc=models.CharField(max_length=500,null=True)

    def __str__(self):
        return self.symptom_name

class Usersymptoms(models.Model):
    check_up_id=models.CharField(max_length=20,null=False)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    my_symptoms=models.ManyToManyField(symptoms)
    timestamp=models.TimeField(default=datetime.now)

class Checkup(models.Model):
    types=(('DIABETES','DIABETES'),
            ('HEART DISEASE','HEART DISEASE'),
            ('SYMPTOMS CHECK','SYMPTOMS CHECK'))
    checkup_id=models.CharField(max_length=12)
    checkup_user=models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="checkups")
    checkup_date=models.DateTimeField()
    checkup_type=models.CharField(max_length=20,choices=types)
    checkup_details=models.JSONField(null=True)
    is_verified = models.BooleanField(default=False)
    scan_path = models.ImageField(upload_to='ecg scan',null=True)
    verified_by = models.ForeignKey(Doctor, on_delete=models.CASCADE,null=True)
    comments=models.TextField(max_length=250,null=True)
    def get_checkup_type(self):
        return self.checkup_type.lower().capitalize()+' Prediction Test'

    def get_checkup_details(self):
        if self.checkup_details is not None:
            #print(json.loads(self.checkup_details))
            return json.loads(self.checkup_details)
    def get_report_link(self):
        return reverse('patient-report', kwargs={'patient_id': self.checkup_user.p_id, 'checkup_id': self.checkup_id})
    def get_checkup_link(self):
        return reverse('pdfcheckup', kwargs={'patient_id':self.checkup_user.p_id,'checkup_id': self.checkup_id})
    
    def current(self):
        return datetime.now()
    def verify_checkup(self):
        return reverse('verify-checkup', kwargs={'patient_id': self.checkup_user.p_id, 'checkup_id': self.checkup_id})


class Report(models.Model):
    pdf_path=models.CharField(max_length=12)
    generated_on=models.DateTimeField()
    generates=models.OneToOneField(Checkup,on_delete=models.CASCADE) 




    
'''class Disease_prediction(models.Model):
    checkup_id=models.CharField(max_length=12)
    predictor_type=models.CharField(max_length=12)
    is_verified=models.CharField(max_length=12)
    scan_path=models.CharField(max_length=12)
    prediction=models.CharField(max_length=12)
    name_patient=models.ForeignKey(Profile,on_delete=models.CASCADE)
    verified_by=models.ForeignKey(Doctor,on_delete=models.CASCADE)'''


class Mental_health(models.Model):
    intent=models.CharField(max_length=12)
    suggestion=models.CharField(max_length=12)
    score=models.CharField(max_length=12)
    analyse=models.ForeignKey(Profile,on_delete=models.CASCADE)


'''class predict_diabetes(models.Model):
    Glucoselevel=models.CharField(max_length=12)
    Insulin=models.CharField(max_length=12)
    BMI=models.CharField(max_length=12)
    DiabetesPF=models.CharField(max_length=12)
    Age=models.CharField(max_length=12)'''
