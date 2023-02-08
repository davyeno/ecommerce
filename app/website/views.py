from django.shortcuts import render,  redirect
from django.views import View
from ecommerce.views import get_shop_categories
from ecommerce.cart import Cart
from django.contrib import messages

from .models import Components
from .forms import ContactEmailForm

from django.core.mail import send_mail
from django.template.loader import render_to_string

# Create your views here.
class ContactView(View):
    template = 'contact.html'

    def get(self, request):

        faq = Components.objects.filter(parent_name__contains='Question')

        form = ContactEmailForm()

        context = { 'category' : get_shop_categories(),
                    'cart_length' : Cart(request).__len__(),
                    'faq' : faq,
                    'form' : form
                    }


        return render(request, self.template, context)
    
    def post(self, request):

        faq = Components.objects.filter(parent_name__contains='Question')
        form = ContactEmailForm(request.POST)

        if form.is_valid():
            context = {
                'first_name' : form.cleaned_data.get('first_name'),
                'last_name' : form.cleaned_data.get('last_name'),
                'phone' : form.cleaned_data.get('phone'),
                'email' : form.cleaned_data.get('email'),
                'subject' : form.cleaned_data.get('subject'),
                'message' : form.cleaned_data.get('message')
            }
            message_content = render_to_string('contact-email.txt',context)
            
            send_mail(
                subject = form.cleaned_data.get('subject'),
                message = message_content,
                from_email = None,
                recipient_list= ['vietaodaiboutique@gmail.com'],
                fail_silently= False
            )

            form.save()
            messages.success(request, 'Messages sent successfully', extra_tags='success')            
            return redirect('website:contact')

        else:
            messages.error(request, 'Messages sent error', extra_tags='error')
            context = { 'category' : get_shop_categories(),
                    'cart_length' : Cart(request).__len__(),
                    'faq' : faq,
                    'form' : form
                    }

        return render(request, self.template, context)