from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import MINUTES, PeriodicTask, CrontabSchedule, PeriodicTasks
import json
  
# Create your models here.
class medicine_notifications(models.Model):
    message=models.TextField(max_length=200,default='Its Time to take your medicine')
    send_on=models.DateTimeField()
    sent=models.BooleanField(default=False)
    class Meta:
        ordering=['-send_on']

'''    @receiver(post_save,sender=medicine_notifications)
    def notification_handler(sender, instance, created, **kwargs):
        # call group_send function directly to send notificatoions or you can create a dynamic task in celery beat
        if created:
            schedule, created = CrontabSchedule.objects.get_or_create(
                hour=instance.send_on.hour, minute=instance.send_on.minute, day_of_month=instance.send_on.day)
            task = PeriodicTask.objects.create(crontab=schedule, name="broadcast-notification-"+str(
                instance.id), task="notifications.tasks.medicine_notification", args=json.dumps((instance.id,)))


        #if not created:'''
