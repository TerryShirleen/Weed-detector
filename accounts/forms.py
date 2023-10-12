from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *



class RegisterForm(UserCreationForm):
    username = forms.CharField(max_length=150,help_text='',)  # Set help_text to an empty string to hide default help text
    first_name = forms.CharField(max_length=30, help_text='')
    last_name = forms.CharField(max_length=30, help_text='')
    email = forms.EmailField(help_text='')
    password1 = forms.CharField(widget=forms.PasswordInput,help_text='',)
    password2 = forms.CharField(widget=forms.PasswordInput,help_text='',)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['is_approved','status','otp_device']

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(label='Enter OTP', max_length=6, required=True)


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        exclude = ['name']
        