from django.db import models
from django.conf import settings
import uuid
from django.db.models import Q
import datetime
from django.dispatch import receiver

from ecommerce.models import Attribute
from django.contrib.auth.models import User


class Customer(models.Model):
    id = models.BigAutoField(editable=False, primary_key=True, unique=True)
    customer_uuid = models.UUIDField(default=uuid.uuid4, 
                                    editable=False, 
                                    unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    email = models.EmailField(max_length = 254)
    is_subcribe_email = models.BooleanField(default=True)
    is_signup_user = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            blank=True, null=True,
                            on_delete=models.SET_NULL,
                            )
    date_joined = models.DateTimeField(auto_now_add=True)
    date_deleted = models.DateTimeField(blank=True,null=True)
   
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = 'Customers'


@receiver(models.signals.pre_save, sender=Customer, weak=False)
def user_receiver(sender, instance, *args, **kwargs):
    try:
        userprofile = User.objects.get(username=instance.user)
        if userprofile:
            userprofile.first_name = instance.first_name
            userprofile.last_name = instance.last_name
            userprofile.email = instance.email
            userprofile.username = instance.email
            userprofile.save()
    except User.DoesNotExist:
        pass

@receiver(models.signals.pre_delete, sender=settings.AUTH_USER_MODEL, weak=False)
def set_date_deleted_user(sender, instance, *args, **kwargs):
    try:
        instance = Customer.objects.get(email=instance.email)
        if instance:
            instance.date_deleted = datetime.datetime.now()
            instance.is_signup_user = False
            instance.save()
    except Customer.DoesNotExist:
        pass

class Address(models.Model):
    customer_id = models.ForeignKey(Customer,
                                    on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    address_type = models.ForeignKey(Attribute, 
                              limit_choices_to = Q(date_deleted__isnull=True) &
                                                 Q(parent_name__in=['Address Type']),
                              related_name = 'attribute_address',
                              on_delete=models.CASCADE,blank=True,null=True)
    default = models.BooleanField(default=False)
    date_deleted = models.DateTimeField(blank=True,null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_id.email

    class Meta:
        verbose_name_plural = 'Addresses'
