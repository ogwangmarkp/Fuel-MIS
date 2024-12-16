from django.db.models import Q
from .models import AccountsChart, LedgerTransaction, CashAccount, BankAccount, MobileMoneyAccount, SafeAccount, InterBranchTransaction, InterBranchMapping, CashTransfer
from django.db.models import Sum
from datetime import datetime
from companies.models import CompanyBranch
from ledgers.data import system_define_ledgers


def generate_chart_code(parent_id, account_line, company_id):
    code = ''
    if(parent_id > 0):
        last_child = AccountsChart.objects.filter(parent_id=parent_id).order_by('-id')[:1]
        if(len(last_child) > 0):
            temp_code = last_child[0].code.split('-')
            if len(temp_code) > 1:
                code = int(temp_code[1]) + 1
            else:
                code = int(temp_code[0]) + 1
            code = change_code_octate(code)
        else:
            parent = AccountsChart.objects.get(pk=parent_id)
            temp_code = parent.code.split('-')
            if len(temp_code) > 1:
                code = str(temp_code[1]) + '1'
            else:
                code = str(temp_code[0]) + '1'
    else:
        children = AccountsChart.objects.filter(account_line=account_line, company=company_id, parent_id__isnull=True).order_by('-id')[:1]
        if(len(children) > 0):
            temp_code = children[0].code.split('-')
            if len(temp_code) > 1:
                code = int(temp_code[1]) + 1
            else:
                code = int(temp_code[0]) + 1
            code = change_code_octate(code)
        else:
            account_line_code = get_account_line_code(account_line)
            code = str(account_line_code) + '1'
    return code

#Change code octate if ending with zero to avoid duplication
def change_code_octate(code):
    if code % 10 == 0:
        code = code - 10
        code = code * 10 + 1
    return code

def get_account_lines():
    return ['assets', 'liabilities', 'capital', 'income', 'expenses']

def get_income_statement_lines():
    return ['income', 'expenses']

def get_balance_sheet_lines():
    return ['assets', 'capital', 'liabilities']

def get_account_line_code(account_line):
    codes = {
        'assets': 1,
        'liabilities': 2,
        'capital': 3,
        'income': 4,
        'expenses': 5
    }

    return codes[account_line]

def get_coa_by_code(code, company):
    account = None
    accounts = AccountsChart.objects.filter(code=code, company=company)
    if(len(accounts) > 0):
        account = accounts[0]

    return account

def populate_system_coa(company, user_id):
    for key in system_define_ledgers:
        for ledger in system_define_ledgers[key]:
            name = ledger[0]
            code = ledger[1]
            account_parent = ledger[2]

            account = get_coa_by_code(code, company)
            if account:
                parent = get_coa_by_code(account_parent, company)
                account.code = code
                account.name = name
                if parent:
                    account.parent_id = parent
            else:
                parent = get_coa_by_code(account_parent, company)
                account = AccountsChart(company=company, status='active', code=code, name=name, account_line=key, added_by=user_id)
                if parent:
                    account.parent_id=parent

            account.save()

def get_account_line_keys(account_line):
    keys = {
        'assets': 'ast',
        'liabilities': 'lbt',
        'capital': 'cpt',
        'income': 'inc',
        'expenses': 'exp'
    }

    return keys[account_line]

def pad_reference_number(number):
    number = str(number)
    leading_zeros = 5 - len(number)
    if leading_zeros > 0:
        number = '0' * leading_zeros + number
    
    return number

def generate_reference_no(line, company_id, prefix = None):
    now = datetime.now()
    if not prefix:
        base = get_account_line_keys(line) + '-' + now.strftime("%y%m") + '-'
    else:
        base = prefix + '-' + now.strftime("%y%m") + '-'
    
    last_reference = LedgerTransaction.objects.filter(branch__company__id=company_id, reference_no__icontains=base).order_by('-id')
    new_ref = 1
    if(len(last_reference) > 0):
        new_ref = int(last_reference[0].reference_no.split('-')[-1]) + 1

    return base + pad_reference_number(new_ref)

def sort_key(sub_account):
    sort_criteria = ['assets', 'liabilities', 'capital', 'income', 'expenses']
    return sort_criteria.index(sub_account.account_line)

def get_transactional_charts(company_id, account_line=None, parent_code=None):
    if account_line:
        lines = account_line.split(',')
        transactional_charts = AccountsChart.objects.filter(account_line__in=lines, company__id=company_id, parent_id_id__gte=1, child_accounts__isnull=True).order_by('id')
    else:
        transactional_charts = AccountsChart.objects.filter(company__id=company_id, parent_id_id__gte=1, child_accounts__isnull=True).order_by('id')
        
        # Sort charts.
        transactional_charts = sorted(transactional_charts, key=sort_key)

    if parent_code:
        code_split = parent_code.split('-')
        transactional_charts = transactional_charts.filter(Q(code__startswith=code_split[-1]) | Q(code__startswith=parent_code))

    return transactional_charts
    
def get_chart_of_account_balance_at(chart, branch_id, as_at=None):
    balances = {
        'debits': 0,
        'credits': 0
    }
    branch_id =  str(branch_id).split(',')
    if isinstance(chart, AccountsChart):
        account = chart
    else:
        account = AccountsChart.objects.get(pk=chart)

    if as_at:
        as_at = as_at.split(' ')[0]
        debits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, debit_chart=account, record_date__date__lt=as_at).aggregate(total=Sum('amount'))['total']
    else:
        debits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, debit_chart=account).aggregate(total=Sum('amount'))['total']
    if debits:
        balances['debits'] = debits

    if as_at:
        as_at = as_at.split(' ')[0]
        credits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, credit_chart=account, record_date__date__lt=as_at).aggregate(total=Sum('amount'))['total']
    else:
        credits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, credit_chart=account).aggregate(total=Sum('amount'))['total']
    if credits:
        balances['credits'] = credits

    if account.account_line in ['income', 'liabilities', 'capital']:
        balances['balance'] = f"{balances['credits'] - balances['debits']:,}"
        balances['balance_raw'] = balances['credits'] - balances['debits']
    else:
        balances['balance'] = f"{balances['debits'] - balances['credits']:,}"
        balances['balance_raw'] = balances['debits'] - balances['credits']

    return balances

def get_chart_of_account_balance_between(chart, start, end, branch_id):
    end = end.split(' ')[0]
    start = start.split(' ')[0]
    branch_id =  str(branch_id).split(',')
    balances = {
        'debits': 0,
        'credits': 0
    }
    if isinstance(chart, AccountsChart):
        account = chart
    else:
        account = AccountsChart.objects.get(pk=chart)

    debits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, debit_chart=account, record_date__date__gte=start, record_date__date__lte=end).aggregate(total=Sum('amount'))['total']
    if debits:
        balances['debits'] = debits
    
    credits = LedgerTransaction.objects.filter(trans_type='normal', deleted=False, branch_id__in=branch_id, credit_chart=account, record_date__date__gte=start, record_date__date__lte=end).aggregate(total=Sum('amount'))['total']
    if credits:
        balances['credits'] = credits

    if account.account_line in ['income', 'liabilities', 'capital']:
        balances['balance'] = f"{balances['credits'] - balances['debits']:,}"
        balances['balance_raw'] = balances['credits'] - balances['debits']
    else:
        balances['balance'] = f"{balances['debits'] - balances['credits']:,}"
        balances['balance_raw'] = balances['debits'] - balances['credits']

    return balances

def get_account_branch(account_id):

    # Check if cash account.
    account = CashAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return account[0].teller.user_branch.id

    # Check if bank account.
    account = BankAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return account[0].branch.id

    # Check if mobile account.
    account = MobileMoneyAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return account[0].branch.id

    # Check if safe account.
    account = SafeAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return account[0].branch.id

    return 'non_cash_account'

def get_moeny_account_type(account_id):

    # Check if cash account.
    account = CashAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return 'cash'

    # Check if bank account.
    account = BankAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return 'bank'

    # Check if mobile account.
    account = MobileMoneyAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return 'mobile_money'

    # Check if safe account.
    account = SafeAccount.objects.filter(chart_id=account_id)
    if len(account) > 0:
        return 'cash'

    return 'non_money_account'

def post_transaction(details):
    credit_chart = AccountsChart.objects.get(pk=details['credit_chart_id'])

    # Generate reference number
    reference_no = generate_reference_no(credit_chart.account_line, details['company_id'], details['ref_no_prefix'])

    # Save transaction
    transaction = LedgerTransaction(amount=details['amount'], heading=details['heading'], record_date=details['record_date'], payment_method=details['payment_method'],voucher_no=details['voucher_no'], reference_no=reference_no, debit_chart_id=details['debit_chart_id'], credit_chart_id=details['credit_chart_id'], branch_id=details['branch_id'], added_by_id=details['user_id'])
    transaction.save()

    return transaction



def reverse_transaction(transaction, user_id,comment=None):
    if not isinstance(transaction, LedgerTransaction):
        transaction = LedgerTransaction.objects.get(pk=transaction)
    
    if transaction.trans_type != 'normal':
        return transaction
    
    # Update original transaction status
    transaction.trans_type = 'reversed'
    transaction.save()

    # Create reversal transaction
    transaction_details = {
        "heading": transaction.heading + ' - reversal',
        "amount": transaction.amount,
        "debit_chart_id": transaction.credit_chart.id,
        "credit_chart_id": transaction.debit_chart.id,
        "payment_method": transaction.payment_method,
        "voucher_no": transaction.voucher_no,
        "branch_id": transaction.branch.id,
        "reference_no": 'rev-' + transaction.reference_no,
        "trans_type": 'reversal',
        "added_by_id": user_id,
        "coment": comment,
        "record_date": transaction.record_date
    }

    # Save general transaction
    transaction = LedgerTransaction(**transaction_details)
    transaction.save()

    return transaction

def update_transaction(transaction, details):
    if not isinstance(transaction, LedgerTransaction):
        transaction = LedgerTransaction.objects.get(pk=transaction)
    
    if transaction.trans_type != 'normal':
        return transaction
    
    # Update original transaction status
    if 'amount' in details.keys():
        transaction.amount = details['amount']

    if 'record_date' in details.keys():
        transaction.record_date = details['record_date']

    if 'coment' in details.keys():
        transaction.coment = details['coment']
        
    transaction.save()

    return transaction

def update_interbranch_transaction(transaction_id, details):
    dest_transaction = InterBranchTransaction.objects.filter(source_transaction_id=transaction_id)
    if len(dest_transaction) > 0:
        update_transaction(dest_transaction[0].dest_transaction, details)
    else:
        source_transaction = InterBranchTransaction.objects.filter(dest_transaction_id=transaction_id)
        if len(source_transaction) > 0:
            update_transaction(source_transaction[0].source_transaction, details)

def delete_transaction(transaction):
    if not isinstance(transaction, LedgerTransaction):
        transaction = LedgerTransaction.objects.get(pk=transaction)
    # Save general transaction
    transaction.delete()

    return 'deleted'

def reverse_interbranch_transaction(transaction_id, user_id):
    dest_transaction = InterBranchTransaction.objects.filter(source_transaction_id=transaction_id)
    
    if len(dest_transaction) > 0:
        reverse_transaction(dest_transaction[0].dest_transaction, user_id)
    else:
        source_transaction = InterBranchTransaction.objects.filter(dest_transaction_id=transaction_id)
        if len(source_transaction) > 0:
            reverse_transaction(source_transaction[0].source_transaction, user_id)

def delete_interbranch_transaction(transaction_id):
    source_transaction = InterBranchTransaction.objects.filter(dest_transaction_id=transaction_id)
    if len(source_transaction) > 0:
        delete_transaction(source_transaction[0].source_transaction)
        source_transaction[0].delete()
    else:
        dest_transaction = InterBranchTransaction.objects.filter(source_transaction_id=transaction_id)
        if len(dest_transaction) > 0:
            delete_transaction(dest_transaction[0].dest_transaction)
            dest_transaction[0].delete()

def update_branch_interbranch_legder(update_branch, user_id):
    parent_chart = 'def-11416'
    branches = CompanyBranch.objects.filter(~Q(id=update_branch.id), company=update_branch.company)
    for branch in branches:
        chart_name = branch.name + ":" + update_branch.name + " - InterBranch"
        mapping = InterBranchMapping.objects.filter(Q(start_branch=update_branch, end_branch=branch) | Q(start_branch=branch, end_branch=update_branch)).first()
        if mapping:
            chart = mapping.chart
            chart.name = chart_name
            chart.save()
        else:
            company = update_branch.company
            parent = get_coa_by_code(parent_chart, company)
            if parent:
                account_line = parent.account_line
                code = generate_chart_code(parent.id, account_line, company.id)

                #Save Cash account chart.
                chart = AccountsChart(name=chart_name, account_line=account_line, company=company, code=code, parent_id=parent, added_by=user_id, allow_sub_accounts=False)
                chart.save()

                mapping = InterBranchMapping(start_branch=branch, end_branch=update_branch, chart=chart, added_by=user_id)
                mapping.save()
                
def reverse_ledger_transaction(transaction, user_id,branch,comment):
    # Update cash transfer is transaction is a cash transfer.
    transfer = CashTransfer.objects.filter(ref_transaction=transaction).first()
    if transfer:
        transfer.approval_status = 'reversed'
        transfer.comment = 'Reversed'
        transfer.approved_by_id = user_id
        transfer.save()
    
    # Reverse InterBranch
    reverse_interbranch_transaction(transaction, user_id)

    # Reverse actual transaction
    return reverse_transaction(transaction, user_id,comment)

def get_inter_branch_chart(branch_one, branch_two):
    chart = None
    mapping = InterBranchMapping.objects.filter(Q(start_branch=branch_one, end_branch=branch_two) | Q(start_branch=branch_two, end_branch=branch_one)).first()
    if mapping:
        chart = mapping.chart

    return chart
