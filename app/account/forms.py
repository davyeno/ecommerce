from faulthandler import disable
from logging import PlaceHolder
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import CharField, TextInput, EmailInput, PasswordInput, EmailField, BooleanField, CheckboxInput
from .models import Customer, Address


class NewUserForm(UserCreationForm):

    error_messages = {
        'username_exist': ("User already exists."),
        'password_mismatch': ("The two password fields didn't match."),
    }
    
    first_name = CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder' : 'First Name',}))
    last_name = CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder' : 'Last Name'}))
    email = EmailField(required=True,
                        max_length=254,
                        help_text='Required. Inform a valid email address.', 
                        widget=EmailInput(attrs={'class': 'form-control', 'placeholder' : 'Email Address'}))
    password1 = CharField(help_text=['Your password must be 8-20 characters long','Contain letters and numbers'],
                          widget=PasswordInput(attrs={'class': 'form-control', 'placeholder' : 'Password'}))
    password2 = CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder' : 'Repeat Password'}))

    class Meta:
        model = User
        fields = ('first_name','last_name', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError(
                self.error_messages['username_exist'],
                code='username_exist',
            )
        return email
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user

class PhoneInput(TextInput):
    input_type = 'tel'
    

class AnonymousCustomerForm(forms.ModelForm):
    first_name = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    last_name = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    email = EmailField(required=True,
                        max_length=254,
                        help_text='Required. Inform a valid email address.', 
                        widget=EmailInput(attrs={'class': 'form-control', }))
    phone_number = CharField(help_text='Format: 777-777-7777',
                             widget=PhoneInput(attrs={'class': 'form-control', 'pattern' : '[0-9]{3}-[0-9]{3}-[0-9]{4}'}))
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone_number', 'email' ]

class ProfileCustomerForm(forms.ModelForm):
    first_name = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    last_name = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    phone_number = CharField(help_text='Format: 777-777-7777',
                             widget=PhoneInput(attrs={'class': 'form-control', 'pattern' : '[0-9]{3}-[0-9]{3}-[0-9]{4}'}))
    
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'phone_number']
    

class AddressForm(forms.ModelForm):
    street_address = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    apartment_address = CharField(widget=TextInput(attrs={'class': 'form-control', 'placeholder' : 'Apt #, Suite, Floor (optional)' }))
    city = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    zip = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    state = CharField(widget=TextInput(attrs={'class': 'form-control', }))
    default = BooleanField(widget=CheckboxInput(attrs={'class': 'custom-control-input', }))

    class Meta:
        model = Address
        fields = ['street_address', 'apartment_address', 'city', 'state', 'zip' , 'default']
    
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['apartment_address'].required = False
        self.fields['default'].required = False

class PasswordResetForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
        'password_duplicate': ("Your new password can't be same as your old password.")
    }
    oldpassword = CharField(widget=PasswordInput(attrs={'class': 'form-control','placeholder' : 'Current Password'}))
    password1 = CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder' : 'Password'}))
    password2 = CharField(widget=PasswordInput(attrs={'class': 'form-control', 'placeholder' : 'Repeat Password'}))

    class Meta:
        model = User
        fields = ('oldpassword','password1', 'password2')
    
    def clean_password2(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")


        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2
    
    def clean(self):
        cleaned_data = super(PasswordResetForm, self).clean()
        oldpassword = cleaned_data.get("oldpassword")
        password2 = cleaned_data.get("password2")
        
 
        if oldpassword and password2 and oldpassword == password2:
            raise forms.ValidationError(
                self.error_messages['password_duplicate'],
                code='password_duplicate',
            )
    

    def save(self, commit=True):
        user = super(PasswordResetForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user
