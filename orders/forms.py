from django import forms
from django.contrib.auth.models import User

# Most of the account forms are built in, but I couldn't find a registration form class
# From https://docs.djangoproject.com/en/2.0/topics/forms/

class RegisterForm(forms.Form):
    username = forms.CharField(label='User name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    firstname = forms.CharField(label='First name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    lastname = forms.CharField(label='Last name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label='Confirm password')
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label='Email address')

    # Make sure the password is typed twice for confirmation
    # From https://docs.djangoproject.com/en/2.0/ref/forms/validation/
    # From https://stackoverflow.com/questions/34609830/django-modelform-how-to-add-a-confirm-password-field
    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("password_confirm")

        if password != confirm_password:
            raise forms.ValidationError('Please make sure that "Password" and "Confirm Password" match')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("The requested user name is already taken.  Please try another name.")