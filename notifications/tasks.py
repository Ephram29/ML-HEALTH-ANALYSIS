from ast import Try
import asyncio
from datetime import datetime
import json
from math import remainder
from celery import shared_task,Celery,states
from healthApp import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from health.models import medicine_prescription,track_medicine
from celery.exceptions import Ignore



@shared_task(bind=True)
def medicine_notification(self,data):
    
    try:
        prescription=medicine_prescription.objects.filter(id=int(data))
        if len(prescription)>0:
            prescription=prescription.first()
            patient = prescription.intake_user
            userid = patient.p_id
            channel_layer=get_channel_layer()
            channel_name="medicine-notificaton-%s"%userid
            msg=prescription.med_time()+'\n'
            for medicine in prescription.medicines.all():
                msg+=medicine.medicine_name.capitalize()
                msg+=','+medicine.med_unit()
                msg+='\n'
                track_medicine(prescription=prescription,medicine_date=datetime.today(),reminder_sent=True,track_for=patient).save()
            loop=asyncio.new_event_loop()
            loop.run_until_complete(channel_layer.group_send(
                channel_name,
                {
                    'type': 'send_medicine_notification',
                    'message': prescription.message,
                    'medicine':msg
                }
            ))
            #prescription.save()
            return "Done"
        else:
            self.update_state(
                state='FAILURE',
                meta={'exe':'Not Found'}
            )
            raise Ignore()
    except:
        self.update_state(
            state='FAILURE',
            meta={'exe': 'Failed'}
        )
        raise Ignore()

