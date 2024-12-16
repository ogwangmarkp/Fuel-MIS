from rest_framework import serializers
from datetime import datetime, timedelta
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from ledgers.models import AccountsChart
from inventory.models import Product, ProductVariation
from users.models import UserVisit,UserLike
from companies.models import Company
from companies.serializers import CompanyAddressSerializer

class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    company_address = CompanyAddressSerializer(many=True, read_only=True)
    visits = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()

    def get_visits(self, obj):
        return UserVisit.objects.filter(resource_id=obj.id,resource_type = 'company').count()
    
    def get_likes(self, obj):
        return UserLike.objects.filter(resource_id=obj.id,resource_type = 'company').count()
    
    class Meta:
        model = Company
        fields = '__all__' 

class PosProductVariationsSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True,source="category.category_name")
    company_name  = serializers.CharField(read_only=True)
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    featured_image_url = serializers.SerializerMethodField()

    def get_featured_image_url(self, obj):
        product_variation = ProductVariation.objects.filter(product__id=obj.id).order_by("id").first()
        if product_variation:
            return product_variation.featured_image_url
        return None
    
    class Meta:
        model = Product
        fields = '__all__'
