import os
from django.db import models
from django.dispatch import receiver
from django.db.transaction import on_commit
from django.db.models import Q

from django.shortcuts import reverse


from django.utils.text import slugify

import string
import random


class Attribute(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    hierarchy_level = models.IntegerField()
    parent_id = models.ForeignKey('self', 
                                  limit_choices_to= {'hierarchy_level': 1},
                                  blank=True, null=True,
                                  on_delete=models.SET_NULL, db_column= 'parent_id')
    parent_name = models.CharField(max_length=100, blank=True, null=True, editable=False)
    date_deleted = models.DateField(blank=True,null=True)
    is_filtered = models.BooleanField()
    presentation = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    hierarchy_level = models.IntegerField()
    parent_id = models.ForeignKey('self', 
                                  limit_choices_to= {'hierarchy_level': 1},
                                  blank=True, null=True,
                                  on_delete=models.SET_NULL, db_column= 'parent_id')
    parent_name = models.CharField(max_length=100, blank=True, null=True, editable=False)
    date_deleted = models.DateField(blank=True,null=True)
    slug_url = models.SlugField(editable=False)

    def __str__(self):
        return self.name

@receiver(models.signals.pre_save, sender=Category, weak=False)
def populate_slug(sender, instance, **kwargs):
    if not instance.slug_url:
        instance.slug_url = slugify(str(instance.name).lower())

@receiver(models.signals.pre_save, sender=Category, weak=False)
@receiver(models.signals.pre_save, sender=Attribute, weak=False)
def parent_category_choices(sender, instance, **kwargs):
    if not instance.parent_id:
        return False
    instance.parent_name = sender.objects.get(name=instance.parent_id).name


def item_dir_url(instance, filename):
    return 'images/{0}/{1}/{2}'.format(instance.category,instance.slug,filename)
  
class Item(models.Model):    
    item_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, unique = True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    discount_price = models.DecimalField(decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, 
                                 limit_choices_to= {'hierarchy_level': 2},
                                 on_delete=models.CASCADE)
    slug = models.SlugField(editable=False)
    details  = models.TextField()
    description = models.TextField()
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_date_time = models.DateTimeField(auto_now=True)
    date_deleted = models.DateField(blank=True,null=True)
    images = models.FileField(upload_to=item_dir_url) 

    def __str__(self):
        return self.title
    
    def filename(self):
        return str(os.path.basename(self.images.name))

def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

@receiver(models.signals.pre_save, sender=Item, weak=False)
def populate_slug(sender, instance, **kwargs):
    if not instance.item_id:
        instance.slug = slugify(instance.title + "-" + str(instance.category) + "-" + rand_slug())
    

def itemimages_dir_url(instance, filename):
    return '{0}/{1}'.format(instance.images_url,filename)

class ItemsImage(models.Model):
    id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_slug = models.CharField(max_length=100, blank=True, null=True, editable=False)
    images_url = models.CharField(max_length=100, blank=True, null=True, editable=False)
    images = models.FileField(upload_to=itemimages_dir_url)
    date_deleted = models.DateField(blank=True,null=True)
    
    class Meta:
        verbose_name_plural = 'Items Images'

@receiver(models.signals.pre_save, sender=ItemsImage, weak=False)
def get_item_slug(sender, instance, **kwargs):
    if not instance.item_id:
        return False
    instance.item_slug = Item.objects.get(title=instance.item_id).slug

@receiver(models.signals.pre_save, sender=ItemsImage, weak=False)
def get_item_image_path(sender, instance, **kwargs):
    if not instance.item_id:
        return False
    
    image_url = Item.objects.get(title=instance.item_id).images
    arr = str(image_url).split('/')
    arr.pop()
    url = '/'.join(arr)

    instance.images_url = url

@receiver(models.signals.post_delete, sender=Item, weak=False)
@receiver(models.signals.post_delete, sender=ItemsImage, weak=False)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.images:
        if os.path.isfile(instance.images.path):
            os.remove(instance.images.path)

@receiver(models.signals.pre_save, sender=Item, weak=False)
@receiver(models.signals.pre_save, sender=ItemsImage, weak=False)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).images
    except Item.DoesNotExist:
        return False

    new_file = instance.images
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            on_commit(lambda: os.remove(old_file.path))

class ItemsInventory(models.Model):
    id = models.BigAutoField(primary_key=True, editable=False, unique=True)
    SKU = models.CharField(max_length=20, editable=False, unique=True)
    item_id = models.ForeignKey(Item, on_delete=models.CASCADE)
    color = models.ForeignKey(Attribute, 
                              limit_choices_to = Q(date_deleted__isnull=True) &
                                                 Q(parent_name__in=['Color','Colors']) &
                                                 Q(is_filtered=True),
                              related_name = 'attribute_color',
                              on_delete=models.CASCADE)
    size = models.ForeignKey(Attribute, 
                             limit_choices_to = Q(date_deleted__isnull=True) &
                                                Q(parent_name__in=['Size','Sizes']) &
                                                Q(is_filtered=True),
                             related_name = 'attribute_size',
                             on_delete=models.CASCADE)
    quantity = models.IntegerField()
    created_date_time = models.DateTimeField(auto_now_add=True)
    modified_date_time = models.DateTimeField(auto_now=True)
    date_deleted = models.DateField(blank=True,null=True)

    
    def __str__(self):
        return '{0}'.format(self.SKU)
    
    class Meta:
        verbose_name_plural = 'Items Inventories'

@receiver(models.signals.pre_save, sender=ItemsInventory, weak=False)
def populate_SKU(sender, instance, **kwargs):
    if not instance.SKU:
        instance.SKU = '{0}{1}{2}{3}'.format(str(instance.item_id.category)[0:2].upper(),instance.color.id,instance.size.id, str(instance.item_id.item_id).zfill(5))


