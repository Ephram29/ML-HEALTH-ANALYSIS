from django.urls import path
from . import views

#from .utilis import update_symptoms

urlpatterns = [
    path('notification',views.notifications_view,name="notification"),
    path('test', views.test, name="test")

    #path('save-symp',update_symptoms,name='symptoms-update'),
]
