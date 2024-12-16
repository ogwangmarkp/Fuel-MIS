from rest_framework import serializers
from .models import *

class ServiceCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(read_only=True, source="parent.category_name")
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class ServiceTagSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(read_only=True, source="parent.tag_name")
    added_by = serializers.CharField(read_only=True)
    class Meta:
        model = ServiceTag
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True,source="category.category_name")
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    featured_image_url = serializers.SerializerMethodField()

    def get_featured_image_url(self, obj):
        service_variation = ServiceVariation.objects.filter(service__id=obj.id).order_by("id").first()
        if service_variation:
            return service_variation.featured_image_url
        return None
    
    class Meta:
        model = Service
        fields = '__all__'


class ServiceVariationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True,source="product.product_name")
    added_by = serializers.CharField(read_only=True)
    
    class Meta:
        model = ServiceVariation
        fields = '__all__'

