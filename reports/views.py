from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from datetime import date, timedelta
from django.db.models import Q, Max
from ledgers.helper import get_transactional_charts, get_account_lines, get_income_statement_lines, get_balance_sheet_lines
from .reports_helper import *
from kwani_api.utils import get_current_user
from ledgers.models import AccountsChart, Currencies
from rest_framework.pagination import PageNumberPagination

class TrialBalanceView(APIView):
  
    def get(self, request, format=None):
        tb_data = {
            'assets': [],
            'liabilities': [],
            'capital': [],
            'income': [],
            'expenses': []
        }
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = self.request.GET.get('branch', None)
        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', None)

        if int(branch_id) == 0:
            branch_id = ',' . join(map(str, CompanyBranch.objects.filter(company__id=company_id).values_list('id', flat=True)))

        #Cash account details
        end = self.request.GET.get('e')
        start =  self.request.GET.get('s')
        coverage = self.request.GET.get('coverage')
        
        # Fetch system charts
        account_lines = get_account_lines()
        for account_line in account_lines:
            accounts = AccountsChart.objects.filter(account_line=account_line, company__id=company_id, parent_id__isnull=True).order_by('code').values('id', 'code', 'name')
            for account in accounts:
                line_charts = get_transactional_charts(company_id, account_line, account['code'])
                transactions = get_chart_child_transactions(line_charts, branch_id, start, end, coverage)
                account['transactions'] = sorted(transactions, key=lambda x: x.get('id', None))

                tb_data[account_line].append(account)
        

        # inject retained earnings
        # Get manual postings
        chart = AccountsChart.objects.filter(code='def-323', company__id=company_id).first()
        chart_transactions = AccountsChartSerializer(
            chart,
            context={
                'branch_id': branch_id,
                'start_date': start,
                'end_date': end,
                'type': 'balanced'
            }
        ).data
                
        # Get automated postings
        end = str(int(start.split('-')[0]) - 1) + '-12-31'
        retained_earnings = get_period_earnings(company_id, branch_id, '2000-01-01', end)
        tb_data = inject_retained_earnings(tb_data, retained_earnings, chart_transactions)
        
        return Response(tb_data, status=status.HTTP_200_OK)
    
class IncomeStatementView(APIView):

    def get(self, request, format=None):
        tb_data = {
            'income': [],
            'expenses': []
        }
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = self.request.GET.get('branch', None)
        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', None)

        if int(branch_id) == 0:
            branch_id = ',' . join(map(str, CompanyBranch.objects.filter(company__id=company_id).values_list('id', flat=True)))

        #Cash account details
        end = self.request.GET.get('e')
        start =  self.request.GET.get('s')
        coverage = self.request.GET.get('coverage')
        
        # Fetch system charts
        account_lines = get_income_statement_lines()
        for account_line in account_lines:
            accounts = AccountsChart.objects.filter(account_line=account_line, company__id=company_id, parent_id__isnull=True).order_by('id').values('id', 'code', 'name')
            
            for account in accounts:
                line_charts = get_transactional_charts(company_id, account_line, account['code'])
                
                transactions = get_chart_child_transactions(line_charts, branch_id, start, end, coverage)
                account['transactions'] = sorted(transactions, key=lambda x: x.get('id', None))
                tb_data[account_line].append(account)
        
        
        return Response(tb_data, status=status.HTTP_200_OK)
    
class BalanceSheetView(APIView):

    def get(self, request, format=None):
        tb_data = {
            'assets': [],
            'capital': [],
            'liabilities': []
        }
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = self.request.GET.get('branch', None)
        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', None)

        if int(branch_id) == 0:
            branch_id = ',' . join(map(str, CompanyBranch.objects.filter(company__id=company_id).values_list('id', flat=True)))

        #Cash account details
        end = self.request.GET.get('e')

        # Use end date for both start and end for Balance Sheet items.
        start =  self.request.GET.get('s')
        coverage = 'balanced'
        
        # Fetch system charts
        account_lines = get_balance_sheet_lines()
        for account_line in account_lines:
            accounts = AccountsChart.objects.filter(account_line=account_line, company__id=company_id, parent_id__isnull=True).order_by('id').values('id', 'code', 'name')
            
            for account in accounts:
                line_charts = get_transactional_charts(company_id, account_line, account['code'])
                
                transactions = get_chart_child_transactions(line_charts, branch_id, start, end, coverage)
                account['transactions'] = sorted(transactions, key=lambda x: x.get('id', None))
                tb_data[account_line].append(account)
        
        
        reference_chart = AccountsChart.objects.filter(code='def-33', company__id=company_id)
        period_earnings = get_period_earnings(company_id, branch_id, start, end)
        if period_earnings['forward'] + period_earnings['btn'] != 0:
            tb_data['capital'][2]['transactions'] = [
                {
                    "id": reference_chart[0].id,
                    "code": "def-33",
                    "name": "Period Net Incomes",
                    "sub_accounts": [
                        {
                            "id": reference_chart[0].id,
                            "code": "def-331",
                            "name": "Current Period Earnings",
                            "balance_bf": {
                                "debits": 0,
                                "credits": 0,
                                "balance": period_earnings['forward'],
                                "balance_raw": period_earnings['forward']
                            },
                            "balance_btn": {
                                "debits": period_earnings['debits'],
                                "credits": period_earnings['credits'],
                                "balance": period_earnings['btn'],
                                "balance_raw": period_earnings['btn']
                            }
                        }
                    ]
                }
            ]

        # inject retained earnings
        # Get manual postings
        chart = AccountsChart.objects.filter(code='def-323', company__id=company_id)
        chart_transactions = AccountsChartSerializer(
            chart[0],
            context={
                'branch_id': branch_id,
                'start_date': start,
                'end_date': end,
                'type': 'balanced'
            }
        ).data
        
        # Get automated postings
        end = str(int(start.split('-')[0]) - 1) + '-12-31'
        retained_earnings = get_period_earnings(company_id, branch_id, '2000-01-01', end)
        tb_data = inject_retained_earnings(tb_data, retained_earnings, chart_transactions)


        return Response(tb_data, status=status.HTTP_200_OK)
