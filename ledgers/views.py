from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .serializers import *
from .models import *
from .helper import *
from kwani_api.utils import get_current_user
from django.utils.timezone import make_aware
from companies.models import CompanyBranch,ServiceClass,CompanyServiceClass
from users.models import UserPermissions
from companies.data import global_settings
from humanresource.models import StaffDeduction,SalaryPayment
class AccountsChartView(viewsets.ModelViewSet):
    serializer_class = AccountsChartSerializer

    def get_queryset(self):
        account_line = self.request.GET.get('line', 'assets')
        company_id = get_current_user(self.request, 'company_id', None)
        return AccountsChart.objects.filter(account_line=account_line, company_id=company_id, parent_id__isnull=True).order_by('id')

    def retrieve(self, request, pk=None):
        instance = AccountsChart.objects.get(pk=pk)
        return Response(self.serializer_class(instance).data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        description = self.request.data.get('description')
        name = self.request.data.get('name')
        account = AccountsChart.objects.get(pk=pk)
        account.description = description
        account.name = name
        account.save()
        return Response(self.serializer_class(account).data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        parent_id = self.request.data.get('parent_id', 0)
        account_line = self.request.data.get('account_line')
        code = generate_chart_code(parent_id, account_line, company_id)

        serializer.save(company=Company.objects.get(pk=company_id), code=code,
                        account_type='user_defined', added_by=self.request.user.id)


class CurrenciesView(viewsets.ModelViewSet):
    serializer_class = CurrenciesSerializer
    queryset = Currencies.objects.all()


class BankAccountView(viewsets.ModelViewSet):
    serializer_class = BankAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        branches = CompanyBranch.objects.filter(
            company__id=company_id).values_list('id', flat=True)
        return BankAccount.objects.filter(branch_id__in=branches)

    def perform_create(self, serializer):
        parent_chart = 'def-11411'
        company_id = get_current_user(self.request, 'company_id', None)
        company = Company.objects.get(pk=company_id)
        bank_name = self.request.data.get('bank_name')
        name = self.request.data.get('name')
        currency = self.request.data.get('currency')
        branch_id = self.request.data.get('branch_id')
        curr_obj = Currencies.objects.filter(id=currency).first()
        alias = f'{curr_obj.symbol} : {bank_name} - {name}'

        # Generate account code for bank account chart.
        parent = get_coa_by_code(parent_chart, company)
        if parent:
            account_line = parent.account_line
            code = generate_chart_code(parent.id, account_line, company_id)
            chart = AccountsChart(name=alias, account_line=account_line, company=company,
                                  code=code, parent_id=parent, added_by=self.request.user.id, has_children=False)
            chart.save()

            serializer.save(chart=chart, alias=alias,
                            branch_id=branch_id, added_by=self.request.user.id)

    def perform_update(self, serializer):
        bank_name = self.request.data.get('bank_name')
        name = self.request.data.get('name')
        currency = self.request.data.get('currency')
        curr_obj = Currencies.objects.filter(id=currency).first()
        alias = f'{curr_obj.symbol} : {bank_name} - {name}'
        account = serializer.save(alias=alias)

        chart = AccountsChart.objects.get(pk=account.chart.id)
        chart.name = name
        chart.save()


class CashAccountView(viewsets.ModelViewSet):
    serializer_class = CashAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        filter_query = self.request.GET.get('filter', None)

        if filter_query == 'list':
            users = User.objects.filter(
                user_branch__company_id=company_id).values_list('id', flat=True)
            return CashAccount.objects.filter(teller_id__in=users)

        return CashAccount.objects.filter(teller__id=self.request.user.id)

    def perform_create(self, serializer):
        parent_chart = 'def-11412'
        company_id = get_current_user(self.request, 'company_id', None)
        company = Company.objects.get(pk=company_id)

        name = self.request.data.get('name')
        parent = get_coa_by_code(parent_chart, company)
        if parent:
            account_line = parent.account_line
            code = generate_chart_code(parent.id, account_line, company_id)

            # Save Cash account chart.
            chart = AccountsChart(name=name, account_line=account_line, company=company,
                                  code=code, parent_id=parent, added_by=self.request.user.id, has_children=False)
            chart.save()
            serializer.save(chart=chart, added_by=self.request.user.id)

    def perform_update(self, serializer):
        name = self.request.data.get('name')
        account = serializer.save()
        chart = AccountsChart.objects.get(pk=account.chart.id)
        chart.name = name
        chart.save()


class SafeAccountView(viewsets.ModelViewSet):
    serializer_class = SafeAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        branches = CompanyBranch.objects.filter(
            company_id=company_id).values_list('id', flat=True)
        return SafeAccount.objects.filter(branch_id__in=branches)

    def perform_create(self, serializer):
        parent_chart = 'def-11412'
        company_id = get_current_user(self.request, 'company_id', None)
        company = Company.objects.get(pk=company_id)
        branch_id = self.request.data.get('branch_id')
        name = self.request.data.get('name')
        parent = get_coa_by_code(parent_chart, company)

        if parent:
            account_line = parent.account_line
            code = generate_chart_code(parent.id, account_line, company_id)
            chart = AccountsChart(name=name, account_line=account_line, company=company,
                                  code=code, parent_id=parent, added_by=self.request.user.id, has_children=False)
            chart.save()

            serializer.save(chart=chart, branch_id=branch_id,
                            added_by=self.request.user.id)

    def perform_update(self, serializer):
        name = self.request.data.get('name')
        account = serializer.save()
        chart = AccountsChart.objects.get(pk=account.chart.id)
        chart.name = name
        chart.save()


class MobileMoneyAccountView(viewsets.ModelViewSet):
    serializer_class = MobileMoneyAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        company_branches = CompanyBranch.objects.filter(
            company_id=company_id).values_list('id', flat=True)
        return MobileMoneyAccount.objects.filter(branch_id__in=company_branches)

    def perform_create(self, serializer):
        parent_chart = 'def-11414'
        company_id = get_current_user(self.request, 'company_id', None)
        company = Company.objects.get(pk=company_id)

        name = self.request.data.get('name')
        branch_id = self.request.data.get('branch_id')

        parent = get_coa_by_code(parent_chart, company)
        if parent:
            account_line = parent.account_line
            code = generate_chart_code(parent.id, account_line, company_id)
            chart = AccountsChart(name=name, account_line=account_line, company=company,
                                  code=code, parent_id=parent, added_by=self.request.user.id, has_children=False)
            chart.save()
            serializer.save(chart=chart, branch_id=branch_id,
                            added_by=self.request.user.id)

    def perform_update(self, serializer):
        name = self.request.data.get('name')
        account = serializer.save()
        chart = AccountsChart.objects.get(pk=account.chart.id)
        chart.name = name
        chart.save()

class ExpenseItemsViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseItemSerializer
    
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return ExpenseItem.objects.filter(**{'branch__id': branch_id}).order_by('-id')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', None)
        serializer.save(branch_id=branch_id, added_by=self.request.user)


class CashTransfersView(viewsets.ModelViewSet):
    serializer_class = CashTransferSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return CashTransfer.objects.filter(branch_id=branch_id).order_by('-id')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', None)
        source_chart_id = self.request.data.get('source_chart')
        destination_chart_id = self.request.data.get('dest_chart')
        cash_transfer_details = serializer.save(
            source_chart_id=source_chart_id, dest_chart_id=destination_chart_id, branch_id=branch_id, added_by=self.request.user)

    ''' def update(self, request, pk=None):
        approval_date = datetime.now().strftime("%Y-%m-%d")
        approval_comment = request.data.get('approval_comment')
        approval_status = request.data.get('approval_status')
        voucher_no = request.data.get('voucher_no')

        #Update Transfer details.
        transfer = CashTransfer.objects.get(pk=pk)

        transaction = None
        if approval_status == 'approved':
            company_id = get_current_user(self.request, 'company_id', None)

            #Generate reference number
            reference_no = generate_reference_no(
                transfer.source_chart.account_line, company_id, 'ch-tr')

            # Get source and destination branches.
            source_branch = get_account_branch(transfer.source_chart.id)
            destination_branch = get_account_branch(
                transfer.destination_chart.id)

            # Same branch transfer.
            if source_branch != 'non_cash_account' and destination_branch != 'non_cash_account' and destination_branch == source_branch:
                transaction = LedgerTransaction(heading=transfer.heading,amount=transfer.amount,voucher_no=voucher_no, record_date=transfer.record_date, reference_no=reference_no,
                                                debit_chart=transfer.destination_chart, credit_chart=transfer.source_chart, branch_id=transfer.branch_id, added_by=transfer.added_by)
                transaction.save()

            # Inter-Branch Transfer
            if source_branch != 'non_cash_account' and destination_branch != 'non_cash_account' and destination_branch != source_branch:
                branches = CompanyBranch.objects.filter(
                    Q(id=destination_branch) | Q(id=source_branch))
                inter_branch_ledger = get_inter_branch_chart(
                    branches[0], branches[1])

                #Interbranch leder should not be null.
                if inter_branch_ledger:
                    transaction = LedgerTransaction(heading=transfer.heading + '-initiated',amount=transfer.amount,voucher_no=voucher_no, record_date=transfer.record_date,
                                                    reference_no=reference_no, debit_chart=inter_branch_ledger, credit_chart=transfer.source_chart, branch_id=source_branch, added_by=transfer.added_by)
                    transaction.save()

                    destination_transaction = LedgerTransaction(heading=transfer.heading + '-received',amount=transfer.amount, voucher_no=voucher_no, record_date=transfer.record_date,
                                                                reference_no=reference_no, debit_chart=transfer.destination_chart, credit_chart=inter_branch_ledger, branch_id=destination_branch, added_by=transfer.added_by)
                    destination_transaction.save()

                    interBranch = InterBranchTransaction(
                        source_transaction=transaction, destination_transaction=destination_transaction, added_by=transfer.added_by)
                    interBranch.save()

        # Update transfer details
        transfer.comment = approval_comment
        transfer.approval_status = approval_status
        transfer.reference_transaction = transaction
        transfer.approved_by = self.request.user
        transfer.date_approved = approval_date
        transfer.save()

        save_user_notification({
            "heading":  "Cash Transfers Approval",
            "message": f"Cash Transfer of Amount: {transfer.amount} from {transfer.source_chart.account_name} to  {transfer.destination_chart.account_name} has been approved by {transfer.approved_by} as at {transfer.record_date.date()}",
            "branch":CompanyBranch.objects.get(pk=transfer.branch.id),
            "branch_name":transfer.branch.name,
            "added_by":transfer.added_by,
            "last_updated_by":transfer.approved_by,
            "key":"ledger_notifications"
        })
        return Response(self.serializer_class(transfer).data, status=status.HTTP_200_OK)
'''


class MyTransfersView(viewsets.ModelViewSet):
    serializer_class = CashTransferSerializer
    http_method_names = ['get', 'put']

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return CashTransfer.objects.filter(branch_id=branch_id, added_by=self.request.user).order_by('-id')

    def update(self, request, pk=None):
        approval_date = datetime.now().strftime("%Y-%m-%d")
        approval_comment = request.data.get('closure_comment')
        transfer = CashTransfer.objects.get(pk=pk)
        transfer.comment = approval_comment
        transfer.approval_status = 'closed'
        transfer.approved_by = self.request.user
        transfer.date_approved = approval_date
        transfer.save()
        return Response(self.serializer_class(transfer).data, status=status.HTTP_200_OK)


class LedgerTransactionsListView(APIView):

    def get(self, request, format=None):
        '''
        Get transactions
        '''
        end = request.GET.get('e', None)
        start = request.GET.get('s', None)
        account = request.GET.get('account', None)
        transaction_type = request.GET.get('type', None)

        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = self.request.GET.get('branch', None)

        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', None)

        if int(branch_id) == 0:
            branch_id = ',' . join(map(str, CompanyBranch.objects.filter(
                company__id=company_id).values_list('id', flat=True)))

        if int(account) > 0:
            transactional_charts = AccountsChart.objects.filter(
                parent_id_id=account)
            if len(transactional_charts) == 0:
                transactional_charts = AccountsChart.objects.filter(id=account)
        else:
            account_line = request.GET.get('line', None)
            transactional_charts = get_transactional_charts(
                company_id, account_line)

        list = AccountsChartSerializer(
            transactional_charts,
            many=True,
            context={
                'branch_id': branch_id,
                'start_date': start,
                'end_date': end,
                'type': transaction_type
            }
        )

        data = {
            'count': len(list.data),
            'results': list.data
        }

        return Response(data, status=status.HTTP_200_OK)


class LedgerTransactionalChartsView(APIView):

    def get(self, request, format=None):
        '''
        Get transactions
        '''
        filter = request.GET.get('filter', None)
        account_line = request.GET.get('line', None)
        company_id = get_current_user(request, 'company_id')

        transactional_charts = get_transactional_charts(
            company_id, account_line)
        if filter == 'agregated':
            parent_accounts = []
            parent_account_ids = []
            for chart in transactional_charts:
                if chart.parent_id.id not in parent_account_ids:
                    parent_accounts.append(chart.parent_id)
                    parent_account_ids.append(chart.parent_id.id)

            parent_accounts = parent_accounts
            transactional_charts = parent_accounts + transactional_charts

        charts = AccountsChartSerializer(transactional_charts, many=True)
        data = {
            'count': len(charts.data),
            'results': charts.data
        }

        return Response(data, status=status.HTTP_200_OK)


class IncomeLedgerTransactionsView(APIView):

    def post(self, request, format=None):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        # Cash account details
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date = self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        pay_method = self.request.data.get('pay_method')
        voucher_no = self.request.data.get('voucher_no')

        valid = True
        account = None
        inter_branch_ledger = None

        if valid:
            credit_chart = AccountsChart.objects.get(pk=credit_chart_id)
            reference_no = generate_reference_no(
                credit_chart.account_line, company_id, 'inc')
            if inter_branch_ledger:
                # Save interbranch transaction
                interbranch_transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method='settlement', voucher_no=voucher_no,
                                                            reference_no=reference_no, debit_chart_id=inter_branch_ledger.id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
                interbranch_transaction.save()

                # Save main transaction
                transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method=pay_method, voucher_no=voucher_no, reference_no=reference_no,
                                                debit_chart_id=debit_chart_id, credit_chart_id=inter_branch_ledger.id, branch_id=account.customer_branch.id, added_by=self.request.user)
                transaction.save()

                interbranch_relation = InterBranchTransaction(
                    source_transaction=transaction, destination_transaction=interbranch_transaction, added_by=self.request.user)
                interbranch_relation.save()
            else:
                # Save transaction
                transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method=pay_method, voucher_no=voucher_no,
                                                reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
                transaction.save()

            data = {
                'message': 'Transaction created.',
                'status': 'success'
            }

        return Response(data, status=status.HTTP_200_OK)


class PostLedgerTransationView(APIView):

    def post(self, request, format=None):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        # Cash account details
        heading = self.request.data.get('heading')
        type = self.request.data.get('type')
        amount = self.request.data.get('amount')
        record_date = self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = self.request.data.get('pay_method')
        voucher_no = self.request.data.get('voucher_no')
        account = None
        inter_branch_ledger = None

        if type == 'cash' or type == 'bank':
            account_balance = get_chart_of_account_balance_at(
                credit_chart_id, branch_id)

            if account_balance['balance_raw'] < float(amount):
                data = {
                    'message': 'Insufficient balance on selected ' + payment_method + ' account.',
                    'status': 'failed'
                }
                Response(data, status=status.HTTP_200_OK)

        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)
        reference_no = generate_reference_no(
            credit_chart.account_line, company_id)
        if inter_branch_ledger:
            if type == 'offset':
                debit_credit_inter_branch = {
                    "debit_chart_id": inter_branch_ledger.id,
                    "credit_chart_id": credit_chart_id
                }

                debit_credit_main = {
                    "debit_chart_id": debit_chart_id,
                    "credit_chart_id": inter_branch_ledger.id
                }
            else:
                debit_credit_inter_branch = {
                    "debit_chart_id": debit_chart_id,
                    "credit_chart_id": inter_branch_ledger.id
                }

                debit_credit_main = {
                    "debit_chart_id": inter_branch_ledger.id,
                    "credit_chart_id": credit_chart_id
                }

            interbranch_transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method='settlement',
                                                        voucher_no=voucher_no, reference_no=reference_no, branch_id=branch_id, added_by=self.request.user, **debit_credit_inter_branch)
            interbranch_transaction.save()

            transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method=payment_method, voucher_no=voucher_no,
                                            reference_no=reference_no, branch_id=account.customer_branch.id, added_by=self.request.user, **debit_credit_main)
            transaction.save()

            interbranch_relation = InterBranchTransaction(
                source_transaction=transaction, destination_transaction=interbranch_transaction, added_by=self.request.user)
            interbranch_relation.save()
        else:
            transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, pay_method=payment_method, voucher_no=voucher_no,
                                            reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
            transaction.save()

        data = {
            'message': 'Transaction created.',
            'status': 'success'
        }

        return Response(data, status=status.HTTP_200_OK)


class ExpenseLedgerTransactionsView(APIView):

    def post(self, request, format=None):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date = self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = self.request.data.get('pay_method')
        voucher_no = self.request.data.get('voucher_no')
        staff_id = self.request.data.get('staff',None)
        source = self.request.data.get('source',None)
        coment = self.request.data.get('coment',None)
        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)
        reference_no = generate_reference_no(
            credit_chart.account_line, company_id, 'exp')
       
        transaction = LedgerTransaction.objects.create(**{
            "amount":amount,
            "heading":heading,
            "coment":coment,
            "record_date":record_date,
            "pay_method":payment_method,
            "voucher_no":voucher_no,
            "reference_no":reference_no,
            "credit_chart_id":credit_chart_id,
            "debit_chart_id":debit_chart_id,
            "branch_id":branch_id,
            "added_by": self.request.user
        })
        
        if staff_id and source == 'staff_deduction':
            StaffDeduction.objects.create(**{
                "user_id":staff_id,
                "status":"approved",
                "transaction": transaction,
                "branch_id":branch_id
            })

        if staff_id and source == 'staff_salary':
            SalaryPayment.objects.create(**{
                "user_id":staff_id,
                "status":"approved",
                "transaction": transaction,
                "branch_id":branch_id
        })
            
        data = {
            'message': 'Transaction created.',
            'status': 'success'
        }

        return Response(data, status=status.HTTP_200_OK)


class PendingExpenseLedgerTransactionsViewset(viewsets.ModelViewSet):
    serializer_class = PendingExpenseSerializer
    search_fields = ['branch',]

    def get_queryset(self):

        company_id = get_current_user(self.request, 'company_id', None)
        start = self.request.GET.get('s', None)
        end = self.request.GET.get('e', None)
        status = self.request.GET.get('status', None)
        branch = self.request.GET.get('branch', None)

        filter_query = {"branch__company__id": company_id}
        if branch:
            filter_query['branch__id'] = branch
        if status == 'pending' or status == 'approved' or status == 'declined':
            filter_query['status'] = status
        if start:
            filter_query['record_date__date__gte'] = start
        if end:
            filter_query['record_date__date__lte'] = end
        return PendingExpense.objects.filter(**filter_query).order_by('-id')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', None)
        payment_method = self.request.data.get('pay_method')
        credit_chart_id = self.request.data.get('credit_chart')
        staff_id = self.request.data.get('staff',None)
        source = self.request.data.get('source',None)
        pay_month = self.request.data.get('pay_month',None)

        if payment_method == 'cash':
            permission = UserPermissions.objects.filter(user_id=self.request.user.id, is_feature_active=True, is_company_comp_active=True,
                                                        is_group_active=True, is_role_component_active=True, is_assigned_group_active=True, key='POST_ALL_BRANCHES_EXPENSES').first()
            if permission:
                cash_account = CashAccount.objects.filter(
                    chart__id=credit_chart_id).first()
                if cash_account:
                    branch_id = cash_account.teller.user_branch.id
        saved_expenses = serializer.save(branch=CompanyBranch(pk=branch_id),
                        added_by=self.request.user)
        
        if staff_id and source == 'staff_deduction':
            StaffDeduction.objects.create(**{
                "user_id":staff_id,
                "pending_expense": saved_expenses,
                "branch_id":branch_id
            })
        
        if staff_id and source == 'staff_salary':
            SalaryPayment.objects.create(**{
                "user_id":staff_id,
                "pending_expense": saved_expenses,
                "branch_id":branch_id
        })

    def perform_update(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)

        approved_expense = serializer.save(
            last_updated_by=self.request.user, last_updated=datetime.now())
        
        staff_deduction = StaffDeduction.objects.filter(pending_expense__id=approved_expense.id).first()
        salary_payment = SalaryPayment.objects.filter(pending_expense__id=approved_expense.id).first()

        if approved_expense.status == 'approved':
            credit_chart = None
            debit_chart = AccountsChart.objects.get(
                pk=approved_expense.debit_chart.id)
            credit_chart = AccountsChart.objects.get(
                pk=approved_expense.credit_chart.id)

            reference_no = generate_reference_no(
                credit_chart.account_line, company_id, 'exp')
            
            transaction = LedgerTransaction.objects.create(**{
                "amount":approved_expense.amount,
                "heading":approved_expense.heading,
                "coment":approved_expense.comment,
                "record_date":approved_expense.record_date,
                "pay_method":approved_expense.pay_method,
                "voucher_no":approved_expense.voucher_no,
                "reference_no":reference_no,
                "credit_chart":credit_chart,
                "debit_chart":debit_chart,
                "branch_id":approved_expense.branch.id,
                "added_by": self.request.user
            })

            if staff_deduction:
                staff_deduction.transaction = transaction
                staff_deduction.status = 'approved'
                staff_deduction.save()
            
            print("salary_payment",salary_payment)
            if salary_payment:
                salary_payment.transaction = transaction
                salary_payment.status = 'approved'
                salary_payment.save()
                print("transaction ------",transaction)

        if approved_expense.status == 'declined':
            if staff_deduction:
                staff_deduction.status = 'declined'
                staff_deduction.save()

            if salary_payment:
                salary_payment.status = 'declined'
                salary_payment.save()


class AdvanvedTransactionsView(viewsets.ModelViewSet):
    serializer_class = LedgerTransactionSerializer
    queryset = LedgerTransaction.objects.all()
    http_method_names = ['post', 'put']

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')

        source_branch = get_account_branch(credit_chart_id)
        destination_branch = get_account_branch(debit_chart_id)

        account = CashAccount.objects.filter(chart_id=credit_chart_id).first()
        if account:
            if int(account.teller.user_branch.id) != int(branch_id):
                branch_id = account.teller.user_branch.id

        account = CashAccount.objects.filter(chart_id=debit_chart_id).first()
        if account:
            if int(account.teller.user_branch.id) != int(branch_id):
                branch_id = account.teller.user_branch.id

        if (source_branch == 'non_cash_account' or destination_branch == 'non_cash_account'):

            payment_method = 'settlement'
            destination_money_account_type = get_moeny_account_type(
                debit_chart_id)
            if destination_money_account_type != 'non_money_account':
                payment_method = destination_money_account_type
            else:
                source_money_account_type = get_moeny_account_type(
                    credit_chart_id)
                if source_money_account_type != 'non_money_account':
                    payment_method = source_money_account_type

            credit_chart = AccountsChart.objects.get(pk=credit_chart_id)
            reference_no = generate_reference_no(
                credit_chart.account_line, company_id)

            serializer.save(pay_method=payment_method, reference_no=reference_no, debit_chart_id=debit_chart_id,
                            credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        else:
            heading = self.request.data.get('heading')
            amount = self.request.data.get('amount')
            record_date = self.request.data.get('record_date')
            payment_method = 'settlement'

            credit_chart = AccountsChart.objects.get(pk=credit_chart_id)
            reference_no = generate_reference_no(
                credit_chart.account_line, company_id)
            serializer.save(pay_method=payment_method, reference_no=reference_no, debit_chart_id=debit_chart_id,
                            credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)

            cash_transfer = CashTransfer(heading=heading, approval_status='approved', reference_transaction=serializer, amount=amount, record_date=record_date,
                                         source_chart_id=credit_chart_id, destination_chart_id=debit_chart_id, branch_id=branch_id, added_by=self.request.user)
            cash_transfer.save()


class SuppliersView(viewsets.ModelViewSet):
    serializer_class = SupplierSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return Supplier.objects.filter(company_id=company_id).order_by('-id')

    def perform_create(self, serializer):
        # in the future when supplier becomes active, 
        # it will only be the supplier to update thier contact information
        company_id = get_current_user(self.request, 'company_id', None)
        data   = self.request.data
        name = data.get('name')
        
        company = Company.objects.get(pk=company_id)
        # Generate account code
        parent_chart = AccountsChart.objects.filter(code='def-212')
        parent_id = parent_chart[0].id
        account_line = 'liabilities'
        code = generate_chart_code(parent_id, account_line, company_id)

        #code = get_coa_by_code(parent_id, account_line, company_id)

        # Fill session company account details
        name = 'Supplier: ' + self.request.data.get('name')
        chart = AccountsChart(name=name, parent_id=parent_chart[0], account_line=account_line, has_children=False,
                                company=company, code=code, account_type='user_defined', added_by=self.request.user.id)
        chart.save()
        if chart:
            # Save Creditor details.
            serializer.save(company_id=company_id,
                            chart_id=chart.id, added_by=self.request.user)


    def perform_update(self, serializer):
        name = 'Supplier: ' + self.request.data.get('name')
        saved_supplier = serializer.save()
        if saved_supplier:
            chart = AccountsChart.objects.filter(id=saved_supplier.chart.id).first()
            chart.name = name
            chart.save()
    
class CreditorsView(viewsets.ModelViewSet):
    serializer_class = CreditorAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return CreditorAccount.objects.filter(company_id=company_id).order_by('-id')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)

        status = self.request.data.get('status')
        if status == 'create':
            company = Company.objects.get(pk=company_id)

            #Generate account code
            parent_chart = AccountsChart.objects.filter(account_code='def-212')
            parent_id = parent_chart[0].id
            account_line = 'liabilities'
            account_code = get_coa_by_code(parent_id, account_line, company_id)

            #Fill session company account details
            account_name = 'Creditor: ' + self.request.data.get('account_name')
            chart = AccountsChart(account_name=account_name,parent_id=parent_chart[0], account_line=account_line, allow_sub_accounts=False, company=company, account_code=account_code, account_type='user_defined', added_by=self.request.user.id)
            chart.save()
            chart_id = chart.id
        else:
            chart_id = self.request.data.get('account_chart')

        #Save Creditor details.
        serializer.save(company_id=company_id, chart_id=chart_id, added_by=self.request.user.id)

    def update(self, request, pk=None):
        description = self.request.data.get('description')
        account_name = self.request.data.get('account_name')
        telephone_number = self.request.data.get('telephone_number')
        chart_id = self.request.data.get('account_chart')

        #Update Creditor details.
        creditor = CreditorAccount.objects.get(pk=pk)
        creditor.description = description
        creditor.account_name = account_name
        creditor.telephone_number = telephone_number
        creditor.chart_id = chart_id
        creditor.save()

        return Response(self.serializer_class(creditor).data, status=status.HTTP_200_OK)

class CreditorSuppliesView(viewsets.ModelViewSet):
    serializer_class = CreditorSuppliesSerializer
    http_method_names = ['post', 'get']

    def get_queryset(self):
        supplies = []
        supplier_id = self.request.GET.get('supplier_id', None)
        supplier = CreditorAccount.objects.filter(id=supplier_id)
        company_id = get_current_user(self.request, 'company_id', None)
        if supplier and supplier[0].company_id == company_id:
            supplies = CreditorSupplies.objects.filter(creditor=supplier[0]).order_by('maturity_date')
        
        return supplies

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        #transaction details
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date =  self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = 'credit'
        voucher_no = self.request.data.get('voucher_no')

        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)

        # Generate reference number
        reference_no = generate_reference_no(credit_chart.account_line, company_id, 'exp')

        # Save transaction
        transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, payment_method=payment_method,voucher_no=voucher_no, reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        transaction.save()

        #Save Creditor details.
        supplier_id = self.request.data.get('supplier_id')
        maturity_date = self.request.data.get('maturity_date')
        serializer.save(creditor_id=supplier_id, maturity_date=maturity_date, reference_transaction=transaction, added_by=self.request.user.id)


'''
  

class CreditorPaymentsView(viewsets.ModelViewSet):
    serializer_class = CreditorPaymentsSerializer
    http_method_names = ['post']

    def get_queryset(self):
        payments = []
        supplies_id = self.request.GET.get('supplies_id', None)
        if supplies_id:
            payments = CreditorPayments.objects.filter(supply_id=supplies_id)
        
        return payments
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        #transaction details
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date =  self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = self.request.data.get('payment_method')
        voucher_no = self.request.data.get('voucher_no')

        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)

        # Generate reference number
        reference_no = generate_reference_no(credit_chart.account_line, company_id, 'exp')

        # Save transaction
        transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, payment_method=payment_method,voucher_no=voucher_no, reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        transaction.save()

        #Save Creditor details.
        supplies_id = self.request.data.get('supplies_id')
        serializer.save(supply_id=supplies_id, reference_transaction=transaction, added_by=self.request.user.id)

class DebtorsView(viewsets.ModelViewSet):
    serializer_class = DebtorAccountSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return DebtorAccount.objects.filter(company_id=company_id).order_by('-id')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)

        status = self.request.data.get('status')
        if status == 'create':
            company = Company.objects.get(pk=company_id)

            #Generate account code
            parent_chart = AccountsChart.objects.filter(account_code='def-113')
            parent_id = parent_chart[0].id
            account_line = 'assets'
            account_code = get_coa_by_code(parent_id, account_line, company_id)

            #Fill session company account details
            account_name = 'Debtor: ' + self.request.data.get('account_name')
            chart = AccountsChart(account_name=account_name,parent_id=parent_chart[0], account_line=account_line, allow_sub_accounts=False, company=company, account_code=account_code, account_type='user_defined', added_by=self.request.user.id)
            chart.save()
            chart_id = chart.id
        else:
            chart_id = self.request.data.get('account_chart')

        #Save Creditor details.
        serializer.save(company_id=company_id, chart_id=chart_id, added_by=self.request.user.id)

    def update(self, request, pk=None):
        description = self.request.data.get('description')
        account_name = self.request.data.get('account_name')
        telephone_number = self.request.data.get('telephone_number')
        chart_id = self.request.data.get('account_chart')

        #Update Creditor details.
        debtor = DebtorAccount.objects.get(pk=pk)
        debtor.description = description
        debtor.account_name = account_name
        debtor.telephone_number = telephone_number
        debtor.chart_id = chart_id
        debtor.save()

        return Response(self.serializer_class(debtor).data, status=status.HTTP_200_OK)
    
class DebtorSuppliesView(viewsets.ModelViewSet):
    serializer_class = DebtorSuppliesSerializer
    http_method_names = ['post', 'get']

    def get_queryset(self):
        supplies = []
        supplier_id = self.request.GET.get('supplier_id', None)
        debtor = DebtorAccount.objects.filter(id=supplier_id)
        company_id = get_current_user(self.request, 'company_id', None)
        if debtor and debtor[0].company_id == company_id:
            supplies = DebtorSupplies.objects.filter(debtor=debtor[0]).order_by('maturity_date')
        
        return supplies

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        #transaction details
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date =  self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = 'credit'
        voucher_no = self.request.data.get('voucher_no')

        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)

        # Generate reference number
        reference_no = generate_reference_no(credit_chart.account_line, company_id, 'inc')

        # Save transaction
        transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, payment_method=payment_method,voucher_no=voucher_no, reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        transaction.save()

        #Save Debtor details.
        debtor_id = self.request.data.get('debtor_id')
        maturity_date = self.request.data.get('maturity_date')
        serializer.save(debtor_id=debtor_id, maturity_date=maturity_date, reference_transaction=transaction, added_by=self.request.user.id)

class DebtorPaymentsView(viewsets.ModelViewSet):
    serializer_class = DebtorPaymentsSerializer
    http_method_names = ['post']

    def get_queryset(self):
        payments = []
        supplies_id = self.request.GET.get('debtor_id', None)
        if supplies_id:
            payments = DebtorPayments.objects.filter(supply_id=supplies_id)
        
        return payments
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        #transaction details
        heading = self.request.data.get('heading')
        amount = self.request.data.get('amount')
        record_date =  self.request.data.get('record_date')
        debit_chart_id = self.request.data.get('debit_chart')
        credit_chart_id = self.request.data.get('credit_chart')
        payment_method = self.request.data.get('payment_method')
        voucher_no = self.request.data.get('voucher_no')

        credit_chart = AccountsChart.objects.get(pk=credit_chart_id)

        # Generate reference number
        reference_no = generate_reference_no(credit_chart.account_line, company_id, 'ast')

        # Save transaction
        transaction = LedgerTransaction(amount=amount, heading=heading, record_date=record_date, payment_method=payment_method,voucher_no=voucher_no, reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        transaction.save()

        #Save Debtor details.
        supplies_id = self.request.data.get('supplies_id')
        serializer.save(supply_id=supplies_id, reference_transaction=transaction, added_by=self.request.user.id)
'''
