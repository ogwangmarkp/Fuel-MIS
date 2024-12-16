from django.db import models
from django.utils import timezone
from companies.models import *

class SystemComponent(models.Model):
    component      =  models.CharField(max_length=255)
    component_desc =  models.TextField()
    type           =  models.CharField(max_length=50, null=True, blank=True)
    key            =  models.CharField(max_length=50, null=True, blank=True)
    date_added     = models.DateTimeField(default = timezone.now)
    parent_component =  models.IntegerField(default='0', null=False, blank=False)
    component_added_by = models.BigIntegerField(),
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"system_component'

class CompanyComponent(models.Model):
    system_component  = models.ForeignKey(SystemComponent, on_delete=models.CASCADE, related_name='system_component')
    company =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='component_company')
    date_added        = models.DateTimeField(default = timezone.now)
    company_component_added_by = models.BigIntegerField(),
    is_active = models.BooleanField(default=False)
    class Meta:
        db_table = 'public\".\"company_component'

# for all components / features assigned to the organisation
class CompanyTypeComponent(models.Model):
    system_component = models.ForeignKey(SystemComponent, on_delete=models.CASCADE, related_name='system_comp')
    comp_company_type    =  models.ForeignKey(CompanyType, on_delete=models.CASCADE, related_name='comp_company_type')
    date_added       = models.DateTimeField(default = timezone.now)
    company_type_comp_added_by = models.BigIntegerField(),
    is_active = models.BooleanField(default=False)
    class Meta:
        db_table = 'public\".\"company_type_component'

class CompanyRight(models.Model):
    id = models.IntegerField(primary_key=True)
    component_id =  models.CharField(max_length=255)
    component   =  models.CharField(max_length=255)
    desc        =  models.CharField(max_length=255)
    type        =  models.CharField(max_length=255)
    key         =  models.CharField(max_length=255)
    date_added  = models.CharField(max_length=255)
    parent      = models.CharField(max_length=255)
    is_active   = models.CharField(max_length=255)
    is_active   = models.CharField(max_length=255)
    company_id      = models.CharField(max_length=255)
    company_name    = models.CharField(max_length=255)
    company_short_name = models.CharField(max_length=255)
    class Meta:
        db_table = 'public\".\"CompanyRight'

# for all roles belonging to an organisation.
class UserGroup(models.Model):
    name          =  models.CharField(max_length=255)
    desc          =  models.TextField(blank=True)
    deleted       =  models.CharField(max_length=5, default='0')
    date_added    = models.DateTimeField(default = timezone.now)
    is_active     = models.BooleanField(default=True)
    group_added_by = models.BigIntegerField()
    user_group_company  =  models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_group_company')
    
    class Meta:
        db_table = 'public\".\"user_group'

# for all features belonging to a group/role.
class RoleComponent(models.Model):
    user_group         =  models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='user_group_previllege')
    company_component  =  models.ForeignKey(CompanyComponent, on_delete=models.CASCADE, related_name='company_component')
    date_added     = models.DateTimeField(default = timezone.now)
    is_active      = models.BooleanField(default=True)
    role_component_added_by = models.BigIntegerField()
    class Meta:
        db_table = 'public\".\"role_component'


class CompanyRightsView(models.Model):
    id = models.IntegerField(primary_key=True)
    component_id =  models.CharField(max_length=255)
    component   =  models.CharField(max_length=255)
    desc        =  models.CharField(max_length=255)
    type        =  models.CharField(max_length=255)
    key         =  models.CharField(max_length=255)
    date_added  = models.CharField(max_length=255)
    parent      = models.CharField(max_length=255)
    is_active   = models.CharField(max_length=255)
    is_component_active   = models.CharField(max_length=255)
    company_id         = models.CharField(max_length=255)
    company_name       = models.CharField(max_length=255)
    company_short_name = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'public\".\"company_rights_view'


