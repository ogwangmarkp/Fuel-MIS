from rest_framework import serializers
from ledgers.helper import get_chart_of_account_balance_at, get_chart_of_account_balance_between
from datetime import datetime, timedelta
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from ledgers.models import AccountsChart

class AccountsChartSerializer(serializers.ModelSerializer):
    balance_bf = serializers.SerializerMethodField(read_only=True)
    balance_between = serializers.SerializerMethodField(read_only=True)
    parent_account = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AccountsChart
        fields = ['id', 'code', 'name', 'balance_bf', 'balance_between', 'parent_account']

    def get_parent_account(self, obj):
        serializer = AccountsChartSerializer(instance=obj.parent_id)
        return serializer.data

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

    def get_balance_between(self, account):
        end = self.context.get('end_date', None)
        start = self.context.get('start_date', None)
        branch_id = self.context.get('branch_id', None)
        type = self.context.get('type', None)

        # Get transactions between date.
        if start and end:
            return get_chart_of_account_balance_between(account, start, end, branch_id)

