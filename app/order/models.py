from django.db import models
from django.db.models import Q
from uuid import uuid4
from datetime import datetime
from django.dispatch import receiver
import secrets


from ecommerce.models import ItemsInventory, Attribute
from account.models import Customer, Address

class Voucher(models.Model):
    name = models.CharField(max_length=220)
    code = models.CharField(max_length=220, unique=True)
    amount = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_deleted = models.DateField(blank=True,null=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    ref_id = models.CharField(unique=True, 
                              max_length=128,
                              editable=False)
    customer_id = models.ForeignKey(Customer,
                                    on_delete=models.CASCADE)
    billing_address = models.ForeignKey(Address, 
                                        limit_choices_to=  Q(date_deleted__isnull=True),
                                        related_name = 'attribute_billing',
                                        null=True, on_delete=models.SET_NULL, blank=True,)
    shipping_address = models.ForeignKey(Address, 
                                        limit_choices_to=  Q(date_deleted__isnull=True),
                                        related_name = 'attribute_shipping', 
                                        null=True, on_delete=models.SET_NULL,blank=True)
    discount_amount = models.DecimalField(decimal_places=2, max_digits=10)
    order_type = models.ForeignKey(Attribute, 
                                    limit_choices_to = Q(date_deleted__isnull=True) &
                                                       Q(parent_name__in=['Order Type']),
                                    on_delete=models.CASCADE)
    shipping_price = models.DecimalField(decimal_places=2 , max_digits=10)
    subtotal = models.DecimalField(decimal_places=2, max_digits=10)
    undiscounted_total = models.DecimalField(decimal_places=2, max_digits=10)
    total_net = models.DecimalField(decimal_places=2, max_digits=10)
    voucher = models.ForeignKey(Voucher, blank=True, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=256, null=True, blank=True)
            

        
    def __str__(self):
        return self.ref_id
    
    def _get_self_pk(self):
        return self.pk
    
    
@receiver(models.signals.pre_save, sender=Order, weak=False)
def get_order_number(sender, instance, **kwargs):
    date = datetime.now().date().strftime(r'%y%m%d')
    if not instance.ref_id:
        if instance.customer_id.is_signup_user:
            # return ref id for signup customer
            instance.ref_id = '{0}-{1}-{2}'.format(str(int(instance.customer_id.is_signup_user)).zfill(1),
                                                    str(date),
                                                    str(secrets.randbelow(999999)).zfill(6))
        else:
            # return ref id for not signup customer
            instance.ref_id = '{0}-{1}-{2}'.format(str(int(instance.customer_id.is_signup_user)).zfill(1),
                                                    str(date),
                                                    str(secrets.randbelow(999999)).zfill(6))

class OrderStatus(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.ForeignKey(Attribute, 
                                limit_choices_to = Q(date_deleted__isnull=True) &
                                                    Q(parent_name__in=['Order Status']),
                                on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=256, null=True, blank=True)
    
    def __str__(self):
        return str(self.order_id.ref_id)

    class Meta:
        verbose_name_plural = 'Order Status'

class OrderItem(models.Model):
    order_item_id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    order_id = models.ForeignKey(Order, 
                                on_delete=models.CASCADE)
    SKU = models.ForeignKey(ItemsInventory, 
                                to_field='SKU', 
                                db_column='SKU',
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(decimal_places=2, max_digits=10, editable=False)
    total_price = models.DecimalField(decimal_places=2, max_digits=10, editable=False)


    def __str__(self):
        return str(self.order_id.ref_id)
    
    class Meta:
        verbose_name_plural = 'Order Items'

@receiver(models.signals.post_save, sender=OrderItem, weak=False)
def auto_update_inv(sender, instance, created, *args, **kwargs):
    if created:
        item_inventory = ItemsInventory.objects.get(SKU=instance.SKU)
        if item_inventory:
            item_inventory.quantity = item_inventory.quantity - instance.quantity
            item_inventory.save()
    

@receiver(models.signals.pre_save, sender=OrderItem, weak=False)
def get_unit_price(sender, instance, **kwargs):
    if instance.SKU:
        instance.unit_price = instance.SKU.item_id.price

@receiver(models.signals.pre_save, sender=OrderItem, weak=False)
def get_total_price(sender, instance, **kwargs):
    if instance.SKU:
        instance.total_price = instance.SKU.item_id.price * instance.quantity