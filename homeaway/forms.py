from django import forms
from .models import Users,Profile,UserImages,UserSocialLinks
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .token import token_generator
import re
from django.contrib.auth import get_user_model


class SignupForm(UserCreationForm):
    password1 = forms.CharField(label='password', widget=forms.PasswordInput(attrs={'class' :'form-control form-control-user'}))
    password2 = forms.CharField(label='confirm password', widget=forms.PasswordInput(attrs={'class': 'form-control form-control-user'}))

    class Meta:
        model= get_user_model()
        fields= ['first_name', 'last_name','gender', 'phone',  'email', 'username', 'password1', 'password2']
        widgets={

            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
             }

    def clean(self):
        cleaned_data = super().clean()
        phones = cleaned_data.get('phone')
        # password2 = cleaned_data.get('password2')
        email = cleaned_data.get('email')
        username= cleaned_data.get('username')
        # if password1 == password2:

        if Users.objects.filter(email=email).exists():
            self.add_error('email', 'Email already exist')

        if Users.objects.filter(username=username).exists():
                self.add_error('username', 'Username already exist choose another one')

        if phones:
            if Users.objects.filter(phone=phones).exists():
                self.add_error('phone', 'Mobile number already exist')
            else:
                rule = '[0-9]{10}'
                match = re.fullmatch(rule, phones)
                if match is None:
                     self.add_error('phone', 'Mobile number must be contain 10digits')

        # We need the user object, so it's an additional parameter

    def send_activation_email(self, request, user):
        current_site = get_current_site(request)
        subject = 'Activate Your Account'
        message = render_to_string(
            'activate_account.html',
            {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            }
        )
        user.email_user(subject, message, html_message=message)

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(label='',widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        )

    password = forms.CharField(label='',widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))




class UserprofileForm(forms.ModelForm):
    first_name = forms.CharField(label='FirstName', widget=forms.TextInput(attrs={'class': 'form-control ',
                                                                                  'placeholder': "Displayed on your public profile, notifications and other places."}))
    last_name = forms.CharField(label='LastName', widget=forms.TextInput(attrs={'class': 'form-control '}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control '}))
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'class': 'form-control '}))
    phone = forms.CharField(required=False,label='Mobile', widget=forms.TextInput(attrs={'class': 'form-control '}))
    dob= forms.DateField(required=False, label='DateOfBirth',widget=forms.SelectDateWidget(years=range(1900, 2100),attrs={'class' :'form-control '}))
    bio= forms.CharField(required=False, label='Bio',widget=forms.Textarea(attrs={'class': 'form-control','rows':'2','cols':'2'}))
    website= forms.URLField(required=False, label='Website',widget=forms.URLInput(attrs={'class': 'form-control'}))
    organisation= forms.CharField(required=False, label='Organization',widget=forms.TextInput(attrs={'class': 'form-control'}))
    location= forms.CharField(required=False, label='Location',widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:

        model = Profile
        # exclude=('user',)
        fields= [ 'first_name', 'last_name', 'email','username', 'phone', 'location', 'dob','bio', 'website',  'organisation']

    def clean(self):
        cleaned_data= super().clean()
        username=cleaned_data.get('username')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        # print(self.instance.user)
        if len(username)<4:
            self.add_error('username', 'Minimum 4 Characters needed')

        if Users.objects.exclude(username=self.instance.user).filter(username=username).exists():
            self.add_error('username', 'Username already exist choose another one')
        if Users.objects.exclude(email=self.instance.user.email).filter(email=email).exists():
            self.add_error('email', 'Email already exist choose another one')
        if phone:

            rule = '[0-9]{10}'
            match = re.fullmatch(rule, phone)
            if match is None:
                self.add_error('phone', 'Mobile number must be contain 10digits')
            else:

                if Users.objects.exclude(phone=self.instance.user.phone).filter(phone=phone).exists():
                    self.add_error('phone', 'Mobile number already exist')


class UserSocialLinksform(forms.ModelForm):
    class Meta:
        model=UserSocialLinks
        fields= ['insta_link', 'fb_link','youtube_link', 'git_link']
        widgets={

            'insta_link': forms.TextInput(attrs={'class':'form-control'}),
            'fb_link': forms.TextInput(attrs={'class': 'form-control'}),
            'youtube_link': forms.TextInput(attrs={'class': 'form-control'}),
            'git_link': forms.TextInput(attrs={'class':'form-control'}),

             }


class PasswordChangeForm(forms.Form):
    CurrentPassword = forms.CharField(required=True,label='Current Password', widget=forms.PasswordInput(attrs={'class': ' form-control', 'placeholder': 'Enter Current Password'}))
    NewPassword = forms.CharField(required=True,label='New Password',widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter New Password'}))
    ConfrimNewPassword = forms.CharField(required=True,label='Confirm New Password',widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Retype New Password'}))


class Password_ResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    # captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    def send_confirm_email(self, request, user):
        current_site = get_current_site(request)
        subject = 'Password Reset request'
        message = render_to_string(
            'PasswordResetrequest.html',
            {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
                "protocol": 'https' if request.is_secure() else 'http'
            }
        )

        user.email_user(subject, message, html_message=message)