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
    pay_month = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sal_staff')
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='sal_branch')
    transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE,null=True, blank=True, related_name='sal_transaction')
    pending_expense = models.ForeignKey(PendingExpense, on_delete=models.CASCADE,null=True, blank=True, related_name='sal_pending_expense')

    class Meta:
        db_table = 'public\".\"salary_payment'


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
    salary_payment  = models.ForeignKey(SalaryPayment, on_delete=models.CASCADE,null=True, blank=True, related_name='sd_pending_expense')

    class Meta:
        db_table = 'public\".\"staff_deduction'



