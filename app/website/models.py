from django.db import models
from django.dispatch import receiver

# Create your models here.
class Components(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    hierarchy_level = models.IntegerField()
    parent_id = models.ForeignKey('self', 
                                  blank=True, null=True,
                                  on_delete=models.SET_NULL, db_column= 'parent_id')
    parent_name = models.CharField(max_length=100, blank=True, null=True, editable=False)
    date_deleted = models.DateField(blank=True,null=True)
    value = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Components'

@receiver(models.signals.pre_save, sender=Components, weak=False)
def components_choices(sender, instance, **kwargs):
    if not instance.parent_id:
        return False
    instance.parent_name = sender.objects.get(name=instance.parent_id).name


class EmailComponent(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length = 254)
    phone = models.CharField(max_length=12)
    subject = models.CharField(max_length = 70)
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name_plural = 'Email Components'