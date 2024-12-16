from rest_framework import serializers
from .models import *
from .helper import *
from customers.serializers import CustomerSerializer

class FeeStructureSerializer(serializers.ModelSerializer):
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    class Meta:
        model = FeeStructure
        fields = '__all__'


class ClassFeeStructureSerializer(serializers.ModelSerializer):
    company = serializers.CharField(read_only=True)
    section = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = ClassFeeStructure
        fields = '__all__'

