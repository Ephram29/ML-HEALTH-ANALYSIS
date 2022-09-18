from django.shortcuts import redirect
from django.contrib import messages
from .models import Profile
def is_patient(view_func):
    def wrapper_func(request,patient_id):
        try:
            user=Profile.objects.get(p_id=patient_id)
            if user.patient==request.user:
                return view_func(request,patient_id)
            else:
                return redirect('home')
        except Profile.DoesNotExist:
            messages.error('No patient Object')
            return redirect('home')
    return wrapper_func
    
