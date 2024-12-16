from django.db import models
from django.utils import timezone

class CompanyType(models.Model):
    company_type =  models.CharField(max_length=100)
    date_added   = models.DateTimeField(default = timezone.now)
    added_by     = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'public\".\"company_type'

class ServiceClass(models.Model):
    name =  models.CharField(max_length=100)
    date_added   = models.DateTimeField(default = timezone.now)
    added_by     = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'public\".\"service_class'


class CompanyRegField(models.Model):
    field_label =  models.CharField(max_length=100)
    date_added = models.DateTimeField(default = timezone.now)
    field_added_by = models.BigIntegerField()
    class Meta:
        db_table = 'public\".\"company_reg_field'

class CompanyTypeField(models.Model):
    company_type =  models.ForeignKey(CompanyType, on_delete=models.CASCADE, related_name='company_type_field')
    company_reg_field  =  models.ForeignKey(CompanyRegField, on_delete=models.CASCADE, related_name='company_reg_field')
    date_added = models.DateTimeField(default = timezone.now)
    company_type_field_added_by = models.BigIntegerField()
   
    class Meta:
        db_table = 'public\".\"company_type_field'

class Company(models.Model):
    name       =  models.CharField(max_length=255)
    telephone  =  models.CharField(max_length=100)
    sms_cost   =  models.FloatField(default=0.0)
    short_name =  models.CharField(max_length=255, null=True, blank=True)
    reg_no  =  models.CharField(max_length=50, null=True, blank=True)
    city    =  models.CharField(max_length=255, null=True, blank=True)
    country =  models.CharField(max_length=255, null=True, blank=True, default='Uganda')
    date_added = models.DateTimeField(default = timezone.now)
    added_by   = models.BigIntegerField(null=True, blank=True)
    status =  models.CharField(max_length=25, default='pending')
    logo_url =  models.TextField(null=True, blank=True)
    company_type  =  models.ForeignKey(CompanyType, on_delete=models.CASCADE, related_name='comp_comp_type',null=True,blank=True)
    email         = models.EmailField(max_length = 50, null=True, blank=True)
    website_url  = models.TextField( null=True, blank=True)

    class Meta:
        db_table = 'public\".\"company'
         

class CompanyFieldMeta(models.Model):
    company_field_label =  models.CharField(max_length=100)
    value    =  models.TextField()
    required = models.CharField(max_length = 10, null=False, blank=False)
    order    = models.CharField(max_length = 10, null=False, blank=False)
    section  = models.CharField(max_length = 2550, null=False, blank=False)
    date_added  = models.DateTimeField(default = timezone.now)
    company_field   =  models.ForeignKey(CompanyTypeField, on_delete=models.CASCADE, related_name='company_field')
    field_company   =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='field_company')
    company_field_added_by =  models.BigIntegerField()
   
    class Meta:
        db_table = 'public\".\"company_field_meta'

class CompanySetting(models.Model):
    setting_key    =  models.CharField(max_length=100)
    setting_value  =  models.TextField()
    date_added     = models.DateTimeField(default = timezone.now)
    company_setting    =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_setting')
    setting_added_by = models.BigIntegerField()
    class Meta:
        db_table = 'public\".\"company_setting'

class CompanyServiceClass(models.Model):
    service_class =  models.ForeignKey(ServiceClass, on_delete=models.CASCADE, related_name='sc_service_class')
    company =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sc_company')
    is_active  =  models.BooleanField(default=True)
    date_added = models.DateTimeField(default = timezone.now)
    added_by   = models.BigIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'public\".\"company_service_class'
        
class CompanyBranch(models.Model):
    name =  models.CharField(max_length=255)
    short_name =  models.CharField(max_length=50, null=True, blank=True)
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    status  =  models.CharField(max_length=25, null=True, blank=True)
    address =  models.CharField(max_length=255, null=True, blank=True)
    company =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_branches')
    inter_branch_chart = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = 'public\".\"company_branch'
    
    def __str__(self):
        return self.name


   