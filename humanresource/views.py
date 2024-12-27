from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
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
from .helper import generate_salary

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

class StaffContractsViewSet(viewsets.ModelViewSet):
    serializer_class = StaffContractSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_q = {'user__user_branch__id':branch_id}
        return StaffContract.objects.filter(**filter_q).order_by('-id')
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

class SalariesViewSet(viewsets.ModelViewSet):
    serializer_class = SalarySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status']

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        end_date   = datetime.strptime(end_date, "%Y-%m-%d").replace(day=1)
        _, last_day = calendar.monthrange(end_date.year, end_date.month)
        end_date = end_date.replace(day=last_day)
        
        filter_q = {
            'contract__user__user_branch__id':branch_id,
            'pay_month__date__gte':start_date,
            'pay_month__date__lte':end_date
            }
        return Salary.objects.filter(**filter_q).order_by('-id')



class SalaryPaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = SalaryPaymentSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
   

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return SalaryPayment.objects.filter(**{'branch__id':branch_id}).order_by('-id')
    

class GeneratePayrollView(APIView):

    def post(self, request, format=None):
            start_date = datetime.strptime(request.data.get('start_date'), "%Y-%m-%d").replace(day=1)
            end_date   = datetime.strptime(request.data.get('end_date'), "%Y-%m-%d").replace(day=1)
            _, last_day = calendar.monthrange(end_date.year, end_date.month)
            end_date = end_date.replace(day=last_day)
            branch_id = get_current_user(self.request, 'branch_id', None)
            filter_q = {'user__user_branch__id':branch_id,"start_date__date__lte":end_date,"end_date__date__gte":end_date}
            contracts =StaffContract.objects.filter(**filter_q).order_by('-id')
            generate_salary(contracts,start_date, end_date,self.request.user)
            
            return Response({"message":"success"})

class CaptureSalriesView(APIView):

    def post(self, request, format=None):
            salaries = request.data.get('salaries', None)
            status = request.data.get('status', None)
            if salaries:
                for salary_data in salaries:
                    salary = Salary.objects.filter(id=salary_data['id']).first()
                    if salary:
                        salary.status = status
                        salary.basic_salary = salary_data['basic_salary']
                        salary.save()
            return Response({"message":"success"})

    
class StaffSalaryBalanceView(APIView):

    def get(self,request):
        branch_id = get_current_user(self.request, 'branch_id', None)
        record_date = self.request.GET.get('record_date', None)
        user_id = self.request.GET.get('user_id', None)
        deductions_total = 0
        salary_total = 0
        payment_total = 0

        if user_id:
            salaries = Salary.objects.filter(
                contract__user__id=user_id,
                # pay_month__date__lte=obj.pay_month,
                status = 'approved').values('contract__user').annotate(
                    total=Sum(Coalesce(F('basic_salary'),0.0))).values('total') 
            
            salary_payment = SalaryPayment.objects.filter(
                user__id=user_id,
                # transaction__record_date__lte=obj.pay_month,
                status = 'approved').values('user').annotate(
                    total=Sum(Coalesce(F('transaction__amount'),0.0))).values('total') 
       
            deductions = StaffDeduction.objects.filter(
                user__id=user_id,
                #transaction__record_date__lte=obj.pay_month,
                status = 'approved').values('user').annotate(
                    total=Sum(Coalesce(F('transaction__amount'),0.0))).values('total') 
            
            if deductions:
                deductions_total = deductions[0]['total']
            
            if salaries:
                salary_total = salaries[0]['total']

            if salary_payment:
                payment_total = payment_total + salary_payment[0]['total']
    
        total = salary_total - (payment_total + deductions_total)

        return Response({"total":total})

