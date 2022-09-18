from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import  User
from django import forms

register_styles={'class':'field'}
class CreateUserForm(UserCreationForm):
    email=forms.EmailField()
    
    class Meta:
        model=User
        fields = ['username', 'email', 'first_name','last_name','password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs["placeholder"]='username'
        self.fields['email'].widget.attrs["placeholder"] = 'email'
        self.fields['first_name'].widget.attrs["placeholder"] = 'First Name'
        self.fields['last_name'].widget.attrs["placeholder"] = 'Last Name'
        self.fields['password1'].widget.attrs["placeholder"] = 'Password'
        self.fields['password2'].widget.attrs["placeholder"] = 'Confirm Password'
        

