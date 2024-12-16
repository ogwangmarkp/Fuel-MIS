from rest_framework import serializers
from users.serializers import UserSerializer
from django.db.models import Q, Sum
from datetime import datetime, timedelta
from .models import *
from companies.serializers import CompanyBranchSerializer
from .helper import get_chart_of_account_balance_at, get_chart_of_account_balance_between

class AccountsChartSerializer(serializers.ModelSerializer):
    code   = serializers.CharField(read_only=True)
    child_accounts = serializers.SerializerMethodField(read_only=True)
    transactions   = serializers.SerializerMethodField(read_only=True)
    company        = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    balance_bf     = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AccountsChart
        fields = '__all__'
    
    def get_child_accounts(self, obj):
        children = AccountsChart.objects.filter(parent_id=obj.id).order_by('id')
        serializer = AccountsChartSerializer(instance=children, many=True)
        return serializer.data

    def get_transactions(self, account):
        transactions = []
        end = self.context.get('end_date', None)
        start = self.context.get('start_date', None)
        branch_id = self.context.get('branch_id', None)

        if branch_id and start and end:
            branch_id = str(branch_id).split(',')
            period_transactions = LedgerTransaction.objects.filter(Q(trans_type='normal'), Q(branch_id__in=branch_id), Q(record_date__date__gte=start), Q(record_date__date__lte=end), Q(debit_chart_id=account.id) | Q(credit_chart_id=account.id), deleted=False).order_by('record_date__date', 'id')
            transactions = LedgerTransactionSerializer(period_transactions, many=True).data

        return transactions

    def get_balance_bf(self, account):
        start = self.context.get('start_date', None)
        branch_id = self.context.get('branch_id', None)
        type = self.context.get('type', None)

        # Get transactions between date.
        if start and type == 'balanced':
            if account.account_line in ['assets', 'liabilities', 'capital']:
                return get_chart_of_account_balance_at(account, branch_id, start)
        
            # get balances for only current year for incomes and expenses
            end = datetime.strptime(start, "%Y-%m-%d") - timedelta(days=1)
            end = end.strftime('%Y-%m-%d')
            start = start.split('-')[0] + '-01-01'
            return get_chart_of_account_balance_between(account, start, end, branch_id)

class LedgerTransactionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    credit_chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    debit_chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    added_by = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    branch = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    teller = serializers.SerializerMethodField(read_only=True)

    def get_teller(self, transaction):
        if transaction.added_by:
            return transaction.added_by.username
        
        return ''

    class Meta:
        model = LedgerTransaction
        fields = '__all__'

class CurrenciesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Currencies
        fields = '__all__'

class BankAccountSerializer(serializers.ModelSerializer):
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    branch = CompanyBranchSerializer(read_only=True, required=False)
    current_bal   = serializers.SerializerMethodField(read_only=True)
    account_alias = serializers.CharField(read_only=True, required=False)
    curr_symbol   = serializers.CharField(source="currency.symbol",read_only=True)

    def get_current_bal(self, bank_account):
        if bank_account.chart:
            account_totals = get_chart_of_account_balance_at(bank_account.chart, bank_account.branch.id)
            return account_totals['balance']
        return 0

    class Meta:
        model = BankAccount
        fields = '__all__'

class SafeAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    branch = CompanyBranchSerializer(read_only=True, required=False)
    curr_symbol = serializers.CharField(source="currency.symbol",read_only=True)
    current_bal = serializers.SerializerMethodField(read_only=True)
    
    def get_current_bal(self, safe_account):
        if safe_account.chart:
            account_totals = get_chart_of_account_balance_at(safe_account.chart, safe_account.branch.id)
            return account_totals['balance']
        return 0 
    
    class Meta:
        model = SafeAccount
        fields = '__all__'

class CashAccountSerializer(serializers.ModelSerializer):
    id            = serializers.IntegerField(read_only=True)
    chart         = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    code          = serializers.CharField(source="chart.code",read_only=True)
    teller_name   = serializers.SerializerMethodField(read_only=True)
    teller_branch = serializers.CharField(source="teller.user_branch.id",read_only=True)
    branch_name   = serializers.CharField(source="teller.user_branch.name",read_only=True)
    curr_symbol   = serializers.CharField(source="currency.symbol",read_only=True)
    current_bal   = serializers.SerializerMethodField(read_only=True)

    def get_current_bal(self, cash_account):
       account_totals = get_chart_of_account_balance_at(cash_account.chart, cash_account.teller.user_branch.id)
       return account_totals['balance']
    
    def get_teller_name(self, cash_account):
        return f"{cash_account.teller.first_name} {cash_account.teller.last_name}"
    
    class Meta:
        model = CashAccount
        fields = '__all__'



class MobileMoneyAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    branch = CompanyBranchSerializer(read_only=True, required=False)
    curr_symbol = serializers.CharField(source="currency.symbol",read_only=True)
    current_bal = serializers.SerializerMethodField(read_only=True)

    def get_current_bal(self, mobile_money_account):
        account_totals = get_chart_of_account_balance_at(mobile_money_account.chart, mobile_money_account.branch.id)
        return account_totals['balance']

    class Meta:
        model = MobileMoneyAccount
        fields = '__all__'



class CashTransferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    source_chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    dest_chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    added_by = serializers.SerializerMethodField(read_only=True, required=False)
    branch = serializers.SerializerMethodField(read_only=True, required=False)
    approved_by = serializers.SerializerMethodField(read_only=True, required=False)

    def get_source_chart_name(self, transfer):
        return transfer.source_chart.name

    def get_dest_chart_name(self, transfer):
        return transfer.destination_chart.name

    def get_added_by(self, transfer):
        return transfer.added_by.username

    def get_branch(self, transfer):
        return transfer.branch.name

    def get_approved_by(self, transfer):
        approver = ''
        if transfer.approved_by:
            approver = transfer.approved_by.username
        
        return approver

    class Meta:
        model = CashTransfer
        fields = '__all__'


class PendingExpenseSerializer(serializers.ModelSerializer):
    added_by = serializers.SerializerMethodField(read_only=True, required=False)
    branch = serializers.SerializerMethodField(read_only=True, required=False)
    transactions = serializers.SerializerMethodField(read_only=True)
    expense_chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    teller_chart_details = serializers.SerializerMethodField(read_only=True, required=False)

    class Meta:
        model = PendingExpense
        fields = '__all__'

    def get_expense_chart_name(self, expense):
        return expense.debit_chart.name
    
    def get_teller_chart_details(self, expense):
        cash_account = CashAccount.objects.filter(chart=expense.credit_chart).first()
        return CashAccountSerializer(cash_account,read_only=True, required=False).data
    

    def get_transactions(self, account):
        transactions = {}
        end = self.context.get('end_date', None)
        start = self.context.get('start_date', None)
        branch_id = self.context.get('branch_id', None)

        # Get transactions between date.
        if branch_id and start and end:
            period_transactions = LedgerTransaction.objects.filter(Q(trans_type='normal'), Q(branch_id=branch_id), Q(record_date__date__gte=start), Q(record_date__date__lte=end), Q(debit_chart_id=account.id) | Q(credit_chart_id=account.id), deleted=False).order_by('record_date__date', 'id')
            transactions = LedgerTransactionSerializer(period_transactions, many=True).data

        return transactions

    def get_added_by(self, expense):
        return expense.added_by.username

    def get_branch(self, expense):
        return expense.branch.name


class SupplierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    
    def get_chart_name(self, account):
        return account.chart.code + ' ' + account.chart.name

    class Meta:
        model = Supplier
        fields = '__all__'


class CreditorAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    organisation = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    total_payables = serializers.SerializerMethodField(read_only=True, required=False)
    total_paid = serializers.SerializerMethodField(read_only=True, required=False)

    def get_total_payables(self, creditor):
        payables = CreditorSupplies.objects.filter(creditor=creditor).aggregate(total=Sum('reference_transaction__amount'))['total']
        return payables if payables else 0

    def get_total_paid(self, creditor):
        paid = CreditorPayments.objects.filter(supply__creditor=creditor).aggregate(total=Sum('reference_transaction__amount'))['total']
        return paid if paid else 0
    
    def get_chart_name(self, account):
        return account.chart.code + ' ' + account.chart.account_name

    class Meta:
        model = CreditorAccount
        fields = '__all__'

class CreditorPaymentsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    reference_transaction = LedgerTransactionSerializer(read_only=True, required=False)
    supply = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    
    class Meta:
        model = CreditorPayments
        fields = '__all__'

class CreditorSuppliesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    reference_transaction = LedgerTransactionSerializer(read_only=True, required=False)
    creditor = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    payments = serializers.SerializerMethodField(read_only=True, required=False)
    
    def get_payments(self, supply):
        payments = CreditorPayments.objects.filter(supply=supply)
        paymentTotals = payments.aggregate(total=Sum('reference_transaction__amount'))['total']
        payments = {
            'total': paymentTotals if paymentTotals else 0,
            'list': CreditorPaymentsSerializer(payments, many=True).data
        }

        return payments
    
    class Meta:
        model = CreditorSupplies
        fields = '__all__'

class ExpenseItemSerializer(serializers.ModelSerializer):
    added_by = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    class Meta:
        model = ExpenseItem
        fields = '__all__'

'''



class DebtorAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    organisation = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    chart = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    chart_name = serializers.SerializerMethodField(read_only=True, required=False)
    total_receivable = serializers.SerializerMethodField(read_only=True, required=False)
    total_paid = serializers.SerializerMethodField(read_only=True, required=False)

    def get_total_receivable(self, debtor):
        receivables = DebtorSupplies.objects.filter(debtor=debtor).aggregate(total=Sum('reference_transaction__amount'))['total']
        return receivables if receivables else 0

    def get_total_paid(self, debtor):
        paid = DebtorPayments.objects.filter(supply__debtor=debtor).aggregate(total=Sum('reference_transaction__amount'))['total']
        return paid if paid else 0
    
    def get_chart_name(self, account):
        return account.chart.account_code + ' ' + account.chart.account_name

    class Meta:
        model = DebtorAccount
        fields = '__all__'

class DebtorPaymentsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    reference_transaction = LedgerTransactionSerializer(read_only=True, required=False)
    supply = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    
    class Meta:
        model = DebtorPayments
        fields = '__all__'

class DebtorSuppliesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    reference_transaction = LedgerTransactionSerializer(read_only=True, required=False)
    debtor = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    payments = serializers.SerializerMethodField(read_only=True, required=False)
    
    def get_payments(self, supply):
        payments = DebtorPayments.objects.filter(supply=supply)
        paymentTotals = payments.aggregate(total=Sum('reference_transaction__amount'))['total']
        payments = {
            'total': paymentTotals if paymentTotals else 0,
            'list': DebtorPaymentsSerializer(payments, many=True).data
        }

        return payments
    
    class Meta:
        model = DebtorSupplies
        fields = '__all__'
'''