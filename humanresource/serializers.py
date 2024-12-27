from rest_framework import serializers
from .models import *
from .helper import *
from customers.serializers import CustomerSerializer
from django.db.models.functions import Coalesce
from django.db.models import F, Sum

class StaffDeductionSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    user = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)

    def get_details(self, obj):
        if obj.transaction:
           return {
               "heading":obj.transaction.heading,
               "amount":obj.transaction.amount,
               "record_date":obj.transaction.record_date,
               "pay_method":obj.transaction.pay_method,
               "comment":obj.transaction.coment,
                "staff":f"{obj.user.first_name} {obj.user.last_name}"
            }
        else:
            return {
               "heading":obj.pending_expense.heading,
               "amount":obj.pending_expense.amount,
               "record_date":obj.pending_expense.record_date,
               "pay_method":obj.pending_expense.pay_method,
               "comment":obj.pending_expense.comment,
               "staff":f"{obj.user.first_name} {obj.user.last_name}"
            }
            
    class Meta:
        model = StaffDeduction
        fields = '__all__'


class StaffContractSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    added_by = serializers.CharField(read_only=True)

    def get_details(self, obj):
        return {
                "staff":f"{obj.user.first_name} {obj.user.last_name}"
            }
            
    class Meta:
        model = StaffContract
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    added_by = serializers.CharField(read_only=True)
    tax = serializers.CharField(read_only=True,source='contract.tax')

    def get_details(self, obj):
        deductions_total = 0
        salary_total = 0
        payment_total = 0

        salaries = Salary.objects.filter(
            contract__user=obj.contract.user,
            pay_month__date__lte=obj.pay_month,
            status = 'approved').values('contract__user').annotate(
                total=Sum(Coalesce(F('basic_salary'),0.0))).values('total') 
        
        salary_payment = SalaryPayment.objects.filter(
            user=obj.contract.user,
            #transaction__record_date__lte=obj.pay_month,
            status = 'approved').values('user').annotate(
                total=Sum(Coalesce(F('transaction__amount'),0.0))).values('total') 
        
        ''' deductions = StaffDeduction.objects.filter(
            user=obj.contract.user,
            pending_expense__record_date__lte=obj.pay_month,
            status = 'approved').values('user').annotate(
                total=Sum(Coalesce(F('pending_expense__amount'),0.0))).values('total') '''
       
        deductions = StaffDeduction.objects.filter(
            user=obj.contract.user,
            transaction__record_date__lte=obj.pay_month,
            status = 'approved').values('user').annotate(
                total=Sum(Coalesce(F('transaction__amount'),0.0))).values('total') 
        
        if deductions:
            deductions_total = deductions[0]['total']
        
        if salaries:
            salary_total = salaries[0]['total']

        if salary_payment:
            payment_total = payment_total + salary_payment[0]['total']
 
        arrears = salary_total - (payment_total + deductions_total + obj.basic_salary)
        total = salary_total - (payment_total + deductions_total)
        print(f'{obj.contract.user.first_name} {obj.contract.user.last_name} - {salary_payment}')
        return {
                "staff":f"{obj.contract.user.first_name} {obj.contract.user.last_name}",
                "deductions":deductions_total,
                "total":total if total > 0 else 0,
                "arrears":arrears if arrears > 0 else 0 
            }
            
    class Meta:
        model = Salary
        fields = '__all__'


class SalaryPaymentSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    user = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)

    def get_details(self, obj):
        if obj.transaction:
           return {
               "heading":obj.transaction.heading,
               "amount":obj.transaction.amount,
               "record_date":obj.transaction.record_date,
               "pay_method":obj.transaction.pay_method,
               "comment":obj.transaction.coment,
                "staff":f"{obj.user.first_name} {obj.user.last_name}"
            }
        else:
            return {
               "heading":obj.pending_expense.heading,
               "amount":obj.pending_expense.amount,
               "record_date":obj.pending_expense.record_date,
               "pay_method":obj.pending_expense.pay_method,
               "comment":obj.pending_expense.comment,
               "staff":f"{obj.user.first_name} {obj.user.last_name}"
            }
            
    class Meta:
        model = SalaryPayment
        fields = '__all__'

