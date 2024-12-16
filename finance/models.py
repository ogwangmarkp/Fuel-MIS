from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company,CompanyBranch
from ledgers.models import LedgerTransaction, AccountsChart
from customers.models import Customer
from results.models import ClassPeriod

class FeeStructure(models.Model):
    fees = models.CharField(max_length = 255)
    section = models.CharField(max_length = 255)
    description = models.TextField(default='', null=True, blank=True)
    deleted =  models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='fs_company')
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fs_addedby')

    def __str__(self):
        return self.fees

    class Meta:
        db_table = 'public\".\"fee_structure'


class ClassFeeStructure(models.Model):
    fees = models.CharField(max_length = 255)
    section = models.CharField(max_length = 255)
    description = models.TextField(default='', null=True, blank=True)
    amount = models.FloatField(default=0)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(default = timezone.now)
    class_period = models.ForeignKey(ClassPeriod, on_delete=models.CASCADE, related_name='cfs_class_period')
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='cfs_fee_structure')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cfs_addedby')

    def __str__(self):
        return self.fees

    class Meta:
        db_table = 'public\".\"class_fee_structure'

