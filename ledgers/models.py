from django.db import models
from django.utils import timezone
from companies.models import Company, CompanyBranch
from users.models import User
from django.conf import settings
from customers.models import Customer


class AccountsChart(models.Model):
    ACCOUNT_LINES = (
        ('assets', 'Assets'),
        ('liabilities', 'Liabilities'),
        ('capital', 'Capital'),
        ('income', 'Income'),
        ('expenses', 'Costs and Expenses')
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    report_level = models.CharField(max_length=25, default='default')
    description = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, default='active')
    account_type = models.CharField(max_length=50, default='system')
    parent_id = models.ForeignKey(
        'AccountsChart', on_delete=models.CASCADE, related_name='child_accounts', null=True, blank=True)
    account_line = models.CharField(max_length=25, choices=ACCOUNT_LINES)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='company_accounts')
    has_children = models.BooleanField(default=True)

    class Meta:
        db_table = 'public\".\"accounts_chart'

    def __str__(self):
        return self.name


class InterBranchMapping(models.Model):
    source_branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                                      related_name='inter_branch_start_branch', null=True, blank=True)
    dest_branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                                    related_name='inter_branch_end_branch', null=True, blank=True)
    chart = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                              related_name='mapping_chart', null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'public\".\"inter_branch_mapping'

    def __str__(self):
        return self.name


class Currencies(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    symbol = models.CharField(max_length=25)
    status = models.CharField(max_length=50, default='active')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"currency'

    def __str__(self):
        return self.name


class BankAccount(models.Model):
    bank_name = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    account_no = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='active')
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE,
                                 related_name='bank_account_currency', null=True, blank=True)
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='bank_account_branch', null=True, blank=True)
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='bank_account_chart')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"bank_account'

    def __str__(self):
        return self.account_name


class CashAccount(models.Model):
    name = models.CharField(max_length=255)
    max_expense = models.FloatField(default=0)
    max_withdraw = models.FloatField(default=0)
    status = models.CharField(max_length=50, default='active')
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE,
                                 related_name='cash_account_currency', null=True, blank=True)
    teller = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cash_account_teller')
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='cash_account_teller_branch')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"cash_account'

    def __str__(self):
        return self.name


class SafeAccount(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='active')
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE,
                                 related_name='safe_account_currency', null=True, blank=True)
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='safe_account_branch', null=True, blank=True)
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='safe_account_chart')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"safe_account'

    def __str__(self):
        return self.name


class MobileMoneyAccount(models.Model):
    name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='active')
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='mm_account_branch', null=True, blank=True)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE,
                                 related_name='mm_account_currency', null=True, blank=True)
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='mm_account_chart')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"mobile_money_account'

    def __str__(self):
        return self.name


class LedgerTransaction(models.Model):
    PAYMENT_OPTIONS = (
        ('offset', 'Offset'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('mobile_money', 'Mobile Money'),
        ('settlement', 'Settlement')
    )

    TRANSACTION_TYPES = (
        ('normal', 'Normal'),
        ('revesal', 'Revesal'),
        ('reversed', 'Reversed')
    )
    amount = models.FloatField()
    heading = models.TextField()
    credit_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='credit_account_chart')
    debit_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='debit_account_chart')
    reference_no = models.CharField(max_length=255, null=True, blank=True)
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='transaction_branch', null=True, blank=True)
    voucher_no = models.CharField(max_length=255, null=True, blank=True)
    pay_method = models.CharField(
        max_length=255, choices=PAYMENT_OPTIONS, default='settlement')
    trans_type = models.CharField(
        max_length=255, choices=TRANSACTION_TYPES, default='normal')
    coment = models.TextField(null=True, blank=True)
    record_date = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='transaction_teller', null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"ledger_transaction'

    def __str__(self):
        return self.heading


class CashTransfer(models.Model):
    APPROVAL_STATUSES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
        ('reversed', 'Reversed')
    )
    amount = models.FloatField()
    heading = models.TextField()
    source_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='transfer_source_chart')
    dest_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='transfer_dest_chart')
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='transfer_branch')
    record_date = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='transfer_teller')
    date_added = models.DateTimeField(default=timezone.now)
    approval_status = models.CharField(
        max_length=25, choices=APPROVAL_STATUSES, default='pending')
    approved_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_transafer_approvals', null=True, blank=True)
    date_approved = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    ref_transaction = models.ForeignKey(
        LedgerTransaction, on_delete=models.CASCADE, related_name='cash_transfers', null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"cash_transfer'

    def __str__(self):
        return self.heading


class Supplier(models.Model):
    REGIONS = (
        ('Central', 'Central'),
        ('Eastern', 'Eastern'),
        ('Western', 'Western'),
        ('Northern', 'Northern')
    )

    name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=100)
    city = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(
        max_length=255, null=True, blank=True, default='Uganda')
    region = models.CharField(
        max_length=255, null=True, blank=True, choices=REGIONS)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=25, default='active')
    logo_url = models.TextField(null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    supply_company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='supply_company',null=True, blank=True)
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='supplier_account_chart')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supplier_added_by')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='supplier_company')
    
    class Meta:
        db_table = 'public\".\"supplier'


class CreditorAccount(models.Model):
    account_name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='creditor_company')
    chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='creditor_account_chart')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"creditor_account'

    def __str__(self):
        return self.account_name


class CreditorSupplies(models.Model):
    creditor = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='supplies_creditor')
    ref_transaction = models.ForeignKey(
        LedgerTransaction, on_delete=models.CASCADE, related_name='credit_transaction')
    maturity_date = models.DateTimeField(default=timezone.now)
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"credit_supplies'

    def __str__(self):
        return self.ref_transaction.heading


class CreditorPayments(models.Model):
    supply = models.ForeignKey(
        CreditorSupplies, on_delete=models.CASCADE, related_name='supplies_payment')
    reference_transaction = models.ForeignKey(
        LedgerTransaction, on_delete=models.CASCADE, related_name='supplies_payment_transaction')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"creditor_payments'

    def __str__(self):
        return self.reference_transaction.heading


'''

    
class CreditorPayment(models.Model):
    supply = models.ForeignKey(CreditorSupplies, on_delete=models.CASCADE, related_name='credit_supplies_payment')
    ref_transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE, related_name='supplies_payment_transaction')
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"creditor_payment'
    
    def __str__(self):
        return self.ref_transaction.heading
    

class DebtorAccount(models.Model):
    account_name =  models.CharField(max_length=255)
    telephone    =  models.CharField(max_length=255)
    description  =  models.TextField(null=True, blank=True)
    company      = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='debtor_company')
    chart        =  models.ForeignKey(AccountsChart, on_delete=models.CASCADE, related_name='debtor_account_chart')
    date_added   = models.DateTimeField(default = timezone.now)
    added_by     = models.BigIntegerField(null=True, blank=True)
    deleted      =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"debtor_account'
    
    def __str__(self):
        return self.account_name
    
class DebtorSupplies(models.Model):
    debtor          = models.ForeignKey(DebtorAccount, on_delete=models.CASCADE, related_name='supplies_debtor')
    ref_transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE, related_name='debtor_transaction')
    maturity_date   =  models.DateTimeField(default = timezone.now)
    date_added      = models.DateTimeField(default = timezone.now)
    added_by        = models.BigIntegerField(null=True, blank=True)
    deleted         =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"debtor_supplies'
    
    def __str__(self):
        return self.ref_transaction.heading
    
class DebtorPayment(models.Model):
    supply          = models.ForeignKey(DebtorSupplies, on_delete=models.CASCADE, related_name='debtor_payment')
    ref_transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE, related_name='debtor_payment_transaction')
    date_added      = models.DateTimeField(default = timezone.now)
    added_by        = models.BigIntegerField(null=True, blank=True)
    deleted         =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"debtor_payment'
    
    def __str__(self):
        return self.ref_transaction.heading 

class CreditorAccounts(models.Model):
    account_name =  models.CharField(max_length=255)
    telephone_number =  models.CharField(max_length=255)
    description =  models.TextField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_creditor')
    chart =  models.ForeignKey(AccountsChart, on_delete=models.CASCADE, related_name='creditor_account_chart')
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"creditor_accounts'
    
    def __str__(self):
        return self.account_name
    
class CreditorSupplies(models.Model):
    creditor = models.ForeignKey(CreditorAccounts, on_delete=models.CASCADE, related_name='supplies_creditor')
    reference_transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE, related_name='credit_transaction')
    maturity_date =  models.DateTimeField(default = timezone.now)
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"credit_supplies'
    
    def __str__(self):
        return self.reference_transaction.heading

    
    
class DebtorPayments(models.Model):
    supply = models.ForeignKey(DebtorSupplies, on_delete=models.CASCADE, related_name='debtor_payment')
    reference_transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE, related_name='debtor_payment_transaction')
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted =  models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"debtor_payments'
    
    def __str__(self):
        return self.reference_transaction.heading
    
'''


class InterBranchTransaction(models.Model):
    source_transaction = models.ForeignKey(
        LedgerTransaction, on_delete=models.CASCADE, related_name='source_transaction')
    dest_transaction = models.ForeignKey(
        LedgerTransaction, on_delete=models.CASCADE, related_name='destination_transaction')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='interbranch_added_by', null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"inter_branch_transaction'


class PendingExpense(models.Model):
    STATUSES = (
        ('approved', 'approved'),
        ('pending', 'pending'),
        ('declined', 'declined')
    )
    heading = models.TextField()
    amount = models.FloatField()
    voucher_no = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUSES, default='pending')
    comment = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(null=True, blank=True)
    record_date = models.DateTimeField(default=timezone.now)
    pay_method = models.CharField(max_length=50)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='expense_added_by', null=True, blank=True)
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_approved_by', null=True, blank=True)
    credit_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='expense_credit_chart', null=True, blank=True)
    debit_chart = models.ForeignKey(
        AccountsChart, on_delete=models.CASCADE, related_name='expense_debit_chart', null=True, blank=True)
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='expense_branch', null=True, blank=True)

    class Meta:
        db_table = 'public\".\"pending_expense'


class ExpenseItem(models.Model):
    name = models.TextField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)
    last_updated = models.DateTimeField(null=True, blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_item_addedby')
    branch = models.ForeignKey(CompanyBranch, on_delete=models.CASCADE,
                               related_name='expense_item_branch', null=True, blank=True)
    class Meta:
        db_table = 'public\".\"expense_item'