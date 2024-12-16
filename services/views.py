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


class ServiceCategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceCategorySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('category_name', )
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return ServiceCategory.objects.filter(**{'company__id':company_id,"deleted":False}).order_by('-id')
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        serializer.save(company_id = company_id,added_by=self.request.user)


class ServiceTagsViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceTagSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('tag_name', )
    def get_queryset(self):
        return ServiceTag.objects.filter(**{"deleted":False}).order_by('tag_name')
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
 

class ServicesViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('service_name', )
    
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return Service.objects.filter(**{'company__id':company_id,"deleted":False}).order_by('-id')
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        serializer.save(company_id = company_id,added_by=self.request.user)


class ServiceVariationsViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceVariationSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('variation_name', )
    
    def get_queryset(self):
        service_id = self.request.query_params.get('service', None)
        if service_id:
            return ServiceVariation.objects.filter(**{'service__id':service_id,"deleted":False}).order_by('-id')
        return ServiceVariation.objects.filter(**{"deleted":False}).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)

            
             
