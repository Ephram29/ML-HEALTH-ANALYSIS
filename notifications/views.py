from django.shortcuts import render,HttpResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
def notifications_view(request):
    return render(request,'current_vitals.html',{
        'room_name':'broadcast'
    })

def test(request):
    channel_layer=get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "notification_broadcast",
        {
            'type':'send_notification',
            'message':'notification'
        }
    )
    return HttpResponse("done")
