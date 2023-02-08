from django import forms
from django.contrib.auth.models import User
from django.forms import CharField, TextInput, EmailInput, EmailField, Textarea
from .models import EmailComponent


class ContactEmailForm(forms.ModelForm):

    error_messages = {
        'subject_require': ("Subject is required"),
        'message_empty': ("Your message is empty"),
    }
    
    first_name = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    last_name = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    email = EmailField(required=True,
                        max_length=254,
                        help_text='Required. Inform a valid email address.', 
                        widget=EmailInput(attrs={'class': 'form-control'}))
    phone = CharField(widget=TextInput(attrs={'class': 'form-control',}))
    subject = CharField(widget=TextInput(attrs={'class': 'form-control'}))
    message = CharField(widget=Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = EmailComponent
        fields = ('first_name','last_name', 'email', 'phone', 'subject', 'message')
    
    def __init__(self, *args, **kwargs):
        super(ContactEmailForm, self).__init__(*args, **kwargs)
        self.fields['phone'].required = True