from django.contrib.auth import get_user_model
from rest_framework import serializers
from users.models import *


class UserSerializer(serializers.ModelSerializer):
    user_branch   = serializers.CharField(required=False,read_only=True)
    password      = serializers.CharField(required=False,read_only=True)
    branch_id     = serializers.CharField(required=False,read_only=True,source="user_branch.id")
    group         = serializers.SerializerMethodField()
    group_name    = serializers.SerializerMethodField()
    fullname      = serializers.SerializerMethodField()

    def get_group(self, obj):
        user_assinged_group = UserAssignedGroup.objects.filter(user=obj).first()
        if user_assinged_group:
            return user_assinged_group.group.id
        return ""
    
    def get_group_name(self, obj):
        user_assinged_group = UserAssignedGroup.objects.filter(user=obj).first()
        if user_assinged_group:
            return user_assinged_group.group.name
        return ""
    
    def get_fullname(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    class Meta:
        model = User
        fields = '__all__'

class StaffAssignedDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffAssignedDepartment
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    staff_number    = serializers.CharField(required=False)
    company         = serializers.CharField(required=False,read_only=True)
    staff_added_by  = serializers.CharField(required=False,read_only=True)
    picture_url     = serializers.ImageField(required=False)
    user = UserSerializer(read_only=True, required=False)
    department = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    

    def get_department(self, obj):
        dept = StaffAssignedDepartment.objects.filter(staff=obj,is_main=True,is_active=True).first()
        if dept:
            return dept.department.id
        else:
            return None
    
    def get_department_name(self, obj):
        dept = StaffAssignedDepartment.objects.filter(staff=obj,is_main=True,is_active=True).first()
        if dept:
            return dept.department.name
        else:
            return None
        
    class Meta:
        model = Staff
        fields = '__all__'


class UserAssignedGroupSerializer(serializers.ModelSerializer):
    assigned_role_added_by =  serializers.CharField(required=False,read_only=True)
    assigned_role  = serializers.CharField(read_only=True, source="assigned_role.id")
    role_name      = serializers.CharField(read_only=True, source="assigned_role.role_name")
    class Meta:
        model = UserAssignedGroup
        fields = '__all__'

class GetFullUserSerializer(serializers.ModelSerializer):
#     user_system_role = UserSystemRolesSerializer(read_only=True, many=True)
      name  = serializers.SerializerMethodField()

      def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
        
      class Meta:
         model = get_user_model()
         fields = ('id','username','is_superuser','is_active','name')

class UserPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermissions
        fields = '__all__'

class UserAPIAppSerializer(serializers.ModelSerializer):
    app_key       = serializers.CharField(read_only=True)
    registered_by = serializers.CharField(read_only=True)

    class Meta:
        model = UserAPIApp
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'

class JobTitleSerializer(serializers.ModelSerializer):
    company = serializers.CharField(read_only=True)

    class Meta:
        model = JobTitle
        fields = '__all__'

class UserLikesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLike
        fields = '__all__'

class UserVisitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVisit
        fields = '__all__'

