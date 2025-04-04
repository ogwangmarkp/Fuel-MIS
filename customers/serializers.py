
from rest_framework import serializers
from .models import *


class CustomerTypeSerializer(serializers.ModelSerializer):
    extra_fields = serializers.SerializerMethodField(read_only=True)
    
    def __str__(self):
        return self.customer_type 
     
    def get_extra_fields(self, customer_type):
        extra_fields = CustomerTypeField.objects.filter(customer_type=customer_type).order_by('field_type')
        return CustomerTypeFieldSerializer(extra_fields, many=True).data
    
    class Meta:
        model = CustomerType
        fields = '__all__'


class CustomerFieldOptionSerializer(serializers.ModelSerializer):
    
    def __str__(self):
        return self.option_label 
     
    class Meta:
        model = CustomerFieldOption
        fields = '__all__'


class CustomerTypeFieldSerializer(serializers.ModelSerializer):
    field_options = serializers.SerializerMethodField(read_only=True)

    def __str__(self):
        return self.label 
    
    def get_field_options(self, field_type):
        options = CustomerFieldOption.objects.filter(field_type=field_type).order_by('field_type')
        return CustomerFieldOptionSerializer(options, many=True).data
    
    class Meta:
        model = CustomerTypeField
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    customer_no = serializers.CharField(read_only=True)
    branch_name = serializers.CharField(read_only=True,source="branch.name")
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = Customer
        fields = '__all__'



