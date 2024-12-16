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


class FeeStructuresViewSet(viewsets.ModelViewSet):
    serializer_class = FeeStructureSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('fees', )
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return FeeStructure.objects.filter(**{'company__id':company_id,"deleted":False}).order_by('fees')
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        serializer.save(company_id = company_id,added_by=self.request.user)


class ClassFeeStructuresViewSet(viewsets.ModelViewSet):
    serializer_class = ClassFeeStructureSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('fees', )

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return ClassFeeStructure.objects.filter(**{'fee_structure__company__id':company_id,"is_active":True}).order_by('fees')
    
    def perform_create(self, serializer):
        fee_structure_id  = self.request.data.get('fee_structure')
        fee_structure = FeeStructure.objects.filter(id=fee_structure_id).first()
        if fee_structure:
            serializer.save(section=fee_structure.section,fees=fee_structure.fees,description=fee_structure.description,added_by=self.request.user)
    
    def perform_update(self, serializer):
        fee_structure_id  = self.request.data.get('fee_structure')
        fee_structure = FeeStructure.objects.filter(id=fee_structure_id).first()
        if fee_structure:
            serializer.save(section=fee_structure.section,fees=fee_structure.fees)
        
