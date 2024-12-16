from rest_framework import serializers
from .models import *
from .helper import *
from customers.serializers import CustomerSerializer

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
               "comment":obj.transaction.comment,
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
               "comment":obj.transaction.comment,
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

