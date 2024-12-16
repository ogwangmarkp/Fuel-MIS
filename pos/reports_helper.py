from .serializers import *
from companies.models import * 
from customers.models import * 
from django.db.models import Count,Sum
from django.db.models import Q
from datetime import datetime
from django.utils.timezone import make_aware
from ledgers.helper import get_transactional_charts
import pandas as pd
from datetime import datetime
from django.conf import settings
import os
import json
from .models import *


def get_chart_child_transactions(line_charts, branch_id, start, end, coverage):
    last_node_transactions = []
    leaf_transactions = AccountsChartSerializer(
        line_charts,
        many=True,
        context={
            'branch_id': branch_id,
            'start_date': start,
            'end_date': end,
            'type': 'balanced'
        }
    ).data

    for account_chart_transaction in leaf_transactions:
        forward = account_chart_transaction['balance_bf']['balance_raw']
        between = account_chart_transaction['balance_between']['balance_raw']
        if ((forward != 0 or between != 0) and coverage == 'balanced') or (account_chart_transaction['balance_between']['balance_raw'] != 0 and coverage != 'balanced'):
            account_index = get_parent_index(account_chart_transaction['parent_account']['id'], last_node_transactions)
            if account_index >= 0:
                last_node_transactions[account_index]['sub_accounts'].append({
                    'id':account_chart_transaction['id'],
                    'code':account_chart_transaction['code'],
                    'name':account_chart_transaction['name'],
                    'balance_bf': account_chart_transaction['balance_bf'],
                    'balance_btn':account_chart_transaction['balance_between']
                })
            else:
                last_node_transactions.append({
                    'id':account_chart_transaction['parent_account']['id'],
                    'code':account_chart_transaction['parent_account']['code'],
                    'name':account_chart_transaction['parent_account']['name'],
                    'sub_accounts':[
                        {
                            'id':account_chart_transaction['id'],
                            'code':account_chart_transaction['code'],
                            'name':account_chart_transaction['name'],
                            'balance_bf': account_chart_transaction['balance_bf'],
                            'balance_btn':account_chart_transaction['balance_between']
                        }
                    ]
                })
    

    for i in range(0, len(last_node_transactions)):
        if len(last_node_transactions[i]['sub_accounts']) == 1:
            last_node_transactions[i]['id'] = last_node_transactions[i]['sub_accounts'][0]['id']
    
    return last_node_transactions

def get_parent_index(parent_id, account_list):
    i = 0
    found = False
    for account in account_list:
        if account['id'] == parent_id:
            found = True
            break
        i = i + 1
    
    if found:
        return i
    
    return -1

def get_period_earnings(organisation_id, branch_id, start, end):
    total_incomes = {
        'forward': 0,
        'btn': 0
    }
    total_expenses = {
        'forward': 0,
        'btn': 0
    }

    # Compute total incomes.
    income_charts = get_transactional_charts(organisation_id, 'income')
    income_balances = AccountsChartSerializer(
        income_charts,
        many=True,
        context={
            'branch_id': branch_id,
            'start_date': start,
            'end_date': end,
            'type': 'balanced'
        }
    ).data
    for income_balance in income_balances:
        total_incomes['forward'] += income_balance['balance_bf']['balance_raw']
        total_incomes['btn'] += income_balance['balance_between']['balance_raw']
    
    # Compute total expenses.
    expense_charts = get_transactional_charts(organisation_id, 'expenses')
    expense_balances = AccountsChartSerializer(
        expense_charts,
        many=True,
        context={
            'branch_id': branch_id,
            'start_date': start,
            'end_date': end,
            'type': 'balanced'
        }
    ).data
    for expense_balance in expense_balances:
        total_expenses['forward'] += expense_balance['balance_bf']['balance_raw']
        total_expenses['btn'] += expense_balance['balance_between']['balance_raw']


    return {
        'debits': round(total_expenses['btn']),
        'credits': round(total_incomes['btn']),
        'forward': round(total_incomes['forward'] - total_expenses['forward']),
        'btn': round(total_incomes['btn'] - total_expenses['btn'])
    }


def inject_retained_earnings(tb_data, retained_earnings, chart_transactions):
    if retained_earnings['forward'] + retained_earnings['btn'] != 0:
        entry = {
            "id": chart_transactions['id'],
            "code": "def-323",
            "name": "Retained Earnings/Capital Reserves",
            "balance_bf": {
                "debits": retained_earnings['debits'] + chart_transactions['balance_bf']['debits'],
                "credits": retained_earnings['credits'] + chart_transactions['balance_bf']['credits'],
                "balance": f"{retained_earnings['btn'] + chart_transactions['balance_bf']['balance_raw']:,}",
                "balance_raw": retained_earnings['btn'] + chart_transactions['balance_bf']['balance_raw']
            },
            "balance_btn": chart_transactions['balance_between']
        }

        parent_added = False
        for x in range(0, len(tb_data['capital'][1]['transactions'])):
            if tb_data['capital'][1]['transactions'][x]['code'] == 'def-32':
                child_added = False
                for y in range(0, len(tb_data['capital'][1]['transactions'][x]['sub_accounts'])):
                    if tb_data['capital'][1]['transactions'][x]['sub_accounts'][y]['code'] == 'def-323':
                        tb_data['capital'][1]['transactions'][x]['sub_accounts'][y] = entry
                        child_added = True
                        break
                    
                if not child_added:
                    tb_data['capital'][1]['transactions'][x]['sub_accounts'].append(entry)
                
                parent_added = True
                break

        if not parent_added:
            tb_data['capital'][1]['transactions'].append({
                    "code": "def-32",
                    "name": "Institutional Capital",
                    "sub_accounts": [
                        entry
                    ]
                }
            )

    return tb_data

