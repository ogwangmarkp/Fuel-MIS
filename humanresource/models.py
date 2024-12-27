from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company,CompanyBranch
from ledgers.models import LedgerTransaction, PendingExpense,AccountsChart
from customers.models import Customer

class SalaryPayment(models.Model):
    STATUSES = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('declined', 'declined')
    )
    status = models.CharField(
        max_length=50, choices=STATUSES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sal_staff')
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='sal_branch')
    transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE,null=True, blank=True, related_name='sal_transaction')
    pending_expense = models.ForeignKey(PendingExpense, on_delete=models.CASCADE,null=True, blank=True, related_name='sal_pending_expense')

    class Meta:
        db_table = 'public\".\"salary_payment'


class StaffContract(models.Model):
    STATUSES = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('declined', 'declined'),
        ('expired', 'expired')
    )
    basic_salary = models.FloatField()
    tax = models.FloatField()
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    is_renewed = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50, choices=STATUSES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scontr_staff')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scontr_addedby')

    class Meta:
        db_table = 'public\".\"staff_contract'

class Salary(models.Model):
    STATUSES = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('declined', 'declined')
    )
    basic_salary = models.FloatField()
    status = models.CharField(
        max_length=50, choices=STATUSES, default='pending')
    pay_month = models.DateTimeField(default=timezone.now)
    contract = models.ForeignKey(StaffContract, on_delete=models.CASCADE,null=True, blank=True, related_name='sal_pending_expense')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sal_addedby')

    class Meta:
        db_table = 'public\".\"salary'

class StaffDeduction(models.Model):
    STATUSES = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('declined', 'declined')
    )
    status = models.CharField(
        max_length=50, choices=STATUSES, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sd_staff')
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='sd_branch')
    transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE,null=True, blank=True, related_name='sd_transaction')
    pending_expense = models.ForeignKey(PendingExpense, on_delete=models.CASCADE,null=True, blank=True, related_name='sd_pending_expense')

    class Meta:
        db_table = 'public\".\"staff_deduction'



