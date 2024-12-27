from django.db import models

# Create your models here.
from django.db import models
from django.db import models
from django.utils import timezone
from django.conf import settings
from companies.models import *

class CustomerType(models.Model):
    customer_type = models.CharField(max_length=100)
    type_key      = models.CharField(max_length=50)
    date_added    = models.DateTimeField(default = timezone.now)
    added_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_type_added_by', null=True, blank=True)
    
    class Meta:
        unique_together = ('customer_type',)
        db_table = 'public\".\"customer_type'


class CustomerTypeField(models.Model):
    FIELDS_TYPE = (('date', 'Date'),
        ('file', 'File'),
        ('text', 'Text'),
        ('number', 'Number'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
        ('textarea', 'Text Area'),
        ('select', 'Select')
    )

    label =  models.CharField(max_length=100)
    abbr  =  models.CharField(max_length=50,null=True, blank=True)
    field_type    = models.CharField(max_length = 25, choices=FIELDS_TYPE, default='text')
    customer_type =  models.ForeignKey(CustomerType, on_delete=models.CASCADE, related_name='customer_type_field')
    date_added    = models.DateTimeField(default = timezone.now)
    added_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_type_field_added_by', null=True, blank=True)
    required      = models.BooleanField(default=False)
    order         = models.IntegerField(default=0)
    date_added    = models.DateTimeField(default = timezone.now)
    is_active     = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('id',)
        db_table = 'public\".\"customer_type_field'


class CustomerFieldOption(models.Model):
    option_label =  models.CharField(max_length=100)
    option_value =  models.CharField(max_length=100)
    is_active    = models.BooleanField(default=True)
    date_added   = models.DateTimeField(default = timezone.now)
    field_type   = models.ForeignKey(CustomerTypeField, on_delete=models.CASCADE, related_name='customer_field_option_field_type')
    added_by     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_field_option_added_by', null=True, blank=True)

    class Meta:
        unique_together = ('option_label', 'field_type','option_value')
        db_table = 'public\".\"customer_field_option'


class Customer(models.Model):
    GENDER = (('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
    ('NA', 'N/A')
    )
    name      = models.CharField(max_length = 255, null=False, blank=False)
    telephone_1     = models.CharField(max_length = 55, null=True, blank=True)
    telephone_2     = models.CharField(max_length = 55, null=True, blank=True)
    has_smartphone  = models.BooleanField(default=True)
    ocupation       = models.CharField(max_length = 55, null=True, blank=True)
    gender          = models.CharField(max_length = 55, null=True, blank=True, choices=GENDER, default='NA')
    nationality     = models.CharField(max_length = 255, default="Ugandan")
    dob = models.DateField(null=True, blank=True)
    nin = models.CharField(max_length=20, null=True, blank=True)
    email  = models.CharField(max_length=255, null=True, blank=True)
    religion  = models.CharField(max_length=255, null=True, blank=True)
    marital_status  = models.CharField(max_length=255, null=True, blank=True)
    status          =  models.CharField(max_length=25, null=True, blank=True)
    profile_url     = models.URLField(max_length = 555,null=True, blank=True)
    signature_url   = models.URLField(max_length = 555,null=True, blank=True)
    customer_no     = models.CharField(max_length = 255, null=False, blank=False)
    customer_old_no = models.CharField(max_length = 255, null=True, blank=True)
    customer_type   = models.CharField(max_length = 255, default="Individual")
    is_deleted      = models.BooleanField(default=False)
    is_member       = models.BooleanField(default=False)
    physical_address = models.TextField(null=True,blank=True)
    vehicle_no   = models.CharField(max_length = 255, null=True,blank=True)
    company         = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customer_company')
    added_by        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_added_by', null=True, blank=True)
    date_added      = models.DateTimeField(default = timezone.now)
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'public\".\"customer'


class CustomerFieldData(models.Model):
    value    =  models.TextField()
    field    =  models.ForeignKey(CustomerTypeField, on_delete=models.CASCADE, related_name='customer_field_customer_type_field')
    customer =  models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_field_customer')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_field_added_by', null=True, blank=True)
   
    class Meta:
        unique_together = ('customer', 'field')
        db_table = 'public\".\"customer_field_data'


