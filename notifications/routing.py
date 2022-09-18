from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/patient-dashboard/(?P<patient_id>\w+)/$', consumers.dashboardConsumer.as_asgi()),
]
