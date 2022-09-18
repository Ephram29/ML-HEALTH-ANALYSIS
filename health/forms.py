from dataclasses import fields
from email.policy import default
from django import forms
from .models import Doctor, Profile
choices_bld=(('A+ve','A+ve'),('A-ve','A-ve'),('B+ve','B+ve'),('B-ve','B-ve'),('AB+ve','AB+ve'),('AB-ve','AB-ve'),('O+ve','O+ve'),('O-ve','0-ve'))
choices_gender=(('Male','Male'),('Female','Female'),('Other','other'))
class DateInput(forms.DateInput):
    input_type = 'date'
class Patientform(forms.ModelForm):
    blood_grp=forms.ChoiceField(choices=choices_bld)
    sex=forms.ChoiceField(choices=choices_gender)
    class Meta:
        model=Profile
        fields= ['p_id','phone','fname','lname','sex','dob','height','weight','blood_grp']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['p_id'].widget.attrs["placeholder"]='Patient ID' 
        self.fields['p_id'].widget.attrs["readonly"] = True
        self.fields['phone'].widget.attrs["placeholder"] ='Phone number'
        self.fields['fname'].widget.attrs["placeholder"]='First Name'  
        self.fields['lname'].widget.attrs["placeholder"]='Last Name'  
        self.fields['sex'].widget.attrs["placeholder"]='Sex' 
        self.fields['dob'].widget.attrs["placeholder"]='Date of Birth'
        self.fields['dob'].widget.attrs["max"] = '2015-12-31'
        self.fields['dob'].widget.attrs["min"] = '1900-12-31'
        self.fields['dob'].widget.attrs["value"] = '2000-12-31'
        self.fields['height'].widget.attrs["value"]=''  
        self.fields['height'].widget.attrs["placeholder"]='Height' 
        self.fields['weight'].widget.attrs["placeholder"]='Weight' 
        self.fields['blood_grp'].widget.attrs["placeholder"]='Blood Group' 

class Doctorform(forms.ModelForm):
    sex=forms.ChoiceField(choices=choices_gender)
    class Meta:
        model=Doctor
        fields= ['d_id','specialization','works_in','phone','sex']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs["placeholder"]='Phone number' 
        self.fields['specialization'].widget.attrs["placeholder"] ='Specialization'
        self.fields['d_id'].widget.attrs["placeholder"]='Doctor ID' 
        self.fields['d_id'].widget.attrs["readonly"] = True
        self.fields['works_in'].widget.attrs["placeholder"]='Works in'  
        self.fields['sex'].widget.attrs["placeholder"]='Sex' 



    

            
            
            
            
