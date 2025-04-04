from rest_framework.views import APIView
from .serializers import *
from .models import *
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from kwani_api.utils import get_current_user
from rest_framework import status
from rest_framework import viewsets
from django.db.models import Q
from .helper import get_customer_next_no
# Create your views here.


class CompanyTypesView(viewsets.ModelViewSet):
    serializer_class = CustomerTypeSerializer
    queryset = CustomerType.objects.all().order_by('-id')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

class CompanyTypeFieldsView(viewsets.ModelViewSet):
    serializer_class = CustomerTypeFieldSerializer
    queryset = CustomerTypeField.objects.all().order_by('-id')

    def get_queryset(self):
        customer_type_id = self.request.query_params.get('customer_type', None)
        if customer_type_id:
            return CustomerTypeField.objects.filter(customer_type__id=customer_type_id).order_by('customer_type')
        return CustomerTypeField.objects.all().order_by('customer_type')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class CustomerFieldOptionsView(viewsets.ModelViewSet):
    serializer_class = CustomerFieldOptionSerializer
    queryset = CustomerFieldOption.objects.all().order_by('-id')

    def get_queryset(self):
        field_type_id = self.request.query_params.get('field_type_id', None)
        if field_type_id:
            return CustomerFieldOption.objects.filter(field_type__id=field_type_id).order_by('field_type')
        return CustomerFieldOption.objects.all().order_by('field_type')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

class CustomersView(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('name', 'email','telephone_1','vehicle_no')
    filterset_fields = ['status']
    ordering_fields = 'name'

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        if company_id:
            return Customer.objects.filter(company__id=company_id).order_by('name')
        return Customer.objects.all().order_by('-id')
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        customer_no = get_customer_next_no(company_id,self.request.data.get('customer_no',None))
        serializer.save(customer_no=customer_no,company=Company.objects.get(pk=company_id),added_by=self.request.user)



