from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import *
from .serializers import *
from datetime import datetime
from rest_framework import status
import json
from django.db.models import Q 
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from kwani_api.utils import get_current_user
from ledgers.models import AccountsChart,LedgerTransaction,CreditorSupplies
from ledgers.helper import generate_reference_no,get_coa_by_code,generate_chart_code


class StaffDeductionsViewSet(viewsets.ModelViewSet):
    serializer_class = StaffDeductionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    
    def get_queryset(self):
        paid_deductions = self.request.GET.get('paid_deductions', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_q = {'branch__id':branch_id}

        #if paid_deductions:
            #filter_q['transaction__isnull'] = False
        return StaffDeduction.objects.filter(**filter_q).order_by('-id')
  

class SalaryPaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryPaymentSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return SalaryPayment.objects.filter(**{'branch__id':branch_id}).order_by('-id')
    
  
          
