from unicodedata import name
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from companies.models import *
from companies.models import *
from systemrights.models import *


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/username/<filename>
    return instance.name + '{0}/profile_pic'


def user_file_storage():
    fs = FileSystemStorage()
    return fs

class JobTitle(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_title_added_by', null=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='job_title_company')

    class Meta:
        db_table = 'public\".\"job_title'

class User(AbstractUser):
    GENDER = (('M', 'Male'),
              ('F', 'Female'),
              ('O', 'Other'),
              )
    USER_TYPE = (('Staff', 'Staff'),
                 ('Contact', 'Contact'),
                 ('Customer', 'Customer'),
                 )
    
    date_added = models.DateTimeField(default=timezone.now)
    updated_password = models.BooleanField(default=False)
    user_added_by = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=25, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    gender = models.CharField(max_length=25, null=True, blank=True)
    user_type = models.CharField(
        max_length=25, choices=USER_TYPE, null=True, blank=True)
    profile_url = models.TextField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    nin = models.CharField(max_length=20, null=True, blank=True)
    passport_number = models.CharField(max_length=50, null=True, blank=True)
    nationality = models.CharField(max_length=255, default="Ugandan")
    marital_status = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    user_branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='usr_branch',null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.username


class UserAssignedGroup(models.Model):
    date_added = models.DateTimeField(default=timezone.now)
    group = models.ForeignKey(
        UserGroup, on_delete=models.CASCADE, related_name='user_assigned_group_group')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_assigned_group_user')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_group_assigned_by')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'public\".\"user_assigned_group'


class UserSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loggedinuser')
    session_token = models.TextField(null=True, blank=True)
    is_switched = models.BooleanField(default=False)
    data = models.JSONField(null=False, blank=False)

    class Meta:
        db_table = 'public\".\"user_session_management'

# view model for all components / permissions assigned to the user within an organisation.


class UserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    permission_id = models.CharField(max_length=255)
    permission = models.CharField(max_length=255)
    desc = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    key = models.CharField(max_length=255)
    company_id = models.CharField(max_length=255)
    date_added = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    assigned_by_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    group_desc = models.CharField(max_length=255)
    is_group_active = models.CharField(max_length=255)
    is_feature_active = models.CharField(max_length=255)
    is_company_comp_active = models.CharField(max_length=255)
    is_role_component_active = models.CharField(max_length=255)
    is_assigned_group_active = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'public\".\"user_permissions_view'


class Staff(models.Model):
    EMPLOYER_TYPE = (('Full Time', 'Full Time'),
                     ('Part Time', 'Part Time'),
                     ('Volunteer', 'Volunteer'),
                     ('Intern', 'Intern')
                    )
    job_title = models.ForeignKey(
        JobTitle, on_delete=models.CASCADE, related_name='staff_job_title', null=True, blank=True)
    employment_type = models.CharField(max_length=25, choices=EMPLOYER_TYPE, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    staff_number = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                             related_name='staff_user', null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='st_company')

    class Meta:
        db_table = 'public\".\"staff'


class UserAPIApp(models.Model):
    app_name = models.CharField(max_length=255, null=True, blank=True)
    app_key = models.CharField(max_length=50, null=True, blank=True)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registered_by')

    class Meta:
        db_table = 'public\".\"user_api_app'


class Department(models.Model):
    DEPARTMENT_TYPE = (('Teaching', 'Teaching'),
                       ('Non-Teaching', 'Non-Teaching'),
                       )
    name = models.CharField(max_length=100)
    abbr = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(
        max_length=25, choices=DEPARTMENT_TYPE, null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dept_added_by', null=True)
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='dept_brnach')

    class Meta:
        db_table = 'public\".\"department'


class StaffAssignedDepartment(models.Model):
    date_added = models.DateTimeField(default=timezone.now)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='staff_dept_dept')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='staff_dept_staff')
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_dept_assigned_by')
    is_active = models.BooleanField(default=True)
    is_main = models.BooleanField(default=True)

    class Meta:
        db_table = 'public\".\"staff_assigned_department'


class UserLike(models.Model):
    resource_type =  models.CharField(max_length=255)
    resource_id   =  models.CharField(max_length=100)
    date_added    = models.DateTimeField(default=timezone.now)
    liked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ul_liked_by')
    
    class Meta:
        db_table = 'public\".\"user_like'

class UserVisit(models.Model):
    resource_type =  models.CharField(max_length=255)
    resource_id   =  models.CharField(max_length=100)
    date_added    = models.DateTimeField(default=timezone.now)
    visit_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uv_visit_by',null=True, blank=True)
    
    class Meta:
        db_table = 'public\".\"user_visit'