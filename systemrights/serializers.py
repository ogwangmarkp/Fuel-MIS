
from rest_framework import serializers
from systemrights.models import *

class CompanyTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompanyType
        fields = '__all__'

class CompanyComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyComponent
        fields = '__all__' 
      
class SystemComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemComponent
        fields = '__all__' 

class UserGroupSerializer(serializers.ModelSerializer):
    user_group_company = serializers.CharField(required=False,read_only=True)
    group_added_by     = serializers.CharField(required=False,read_only=True)
    '''components_count  = serializers.SerializerMethodField()

    def get_components_count(self, obj):
        component_ids = []
        role_components = RoleComponent.objects.filter(user_role=obj,org_component__system_component__is_active=True,is_active=True)
        for role_component in role_components:
              component_ids.append(role_component.org_component.system_component.id)
        modules = SystemComponent.objects.filter(org_id =obj.role_org.id,id__in=component_ids,is_active = True,is_feature_active = True).all()
        return len(modules) '''
    
    class Meta:
        model = UserGroup
        fields = '__all__' 

class RoleComponentSerializer(serializers.ModelSerializer):
    user_role      = serializers.CharField(required=False,read_only=True)
    role_component_added_by  = serializers.CharField(required=False,read_only=True)
    company_component     = serializers.CharField(required=False,read_only=True)
    company_component_id  = serializers.CharField(read_only=True, source="company_component.id")
    class Meta:
        model = RoleComponent
        fields = '__all__' 

