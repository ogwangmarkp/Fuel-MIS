from users.serializers import GetFullUserSerializer,UserPermissionsSerializer,UserAssignedGroupSerializer
from companies.models import *
from users.models import UserSession, UserPermissions, UserAssignedGroup
from rest_framework.pagination import PageNumberPagination
from datetime import datetime
import random
import string

logged_in_user_key = None

def custom_jwt_response_handler(token, user=None, request=None):
    if user is not None:
        user_session = UserSession.objects.filter(user=user, session_token = token).first()
        user_branch  = user.user_branch
        if not user_branch:
            user_branch = CompanyBranch.objects.first()
        company_id   = user_branch.company.id
        branch_id    = user_branch.id
        
        if not user_session:
            UserSession.objects.create(user=user, session_token = token, data={"company_id":company_id, "branch_id":branch_id})
        else:
            user_session.data = {"company_id":company_id, "branch_id":branch_id}
            user_session.save()

    company_settings_list = {}
    company_settings = CompanySetting.objects.filter(company_setting=user_branch.company.id).all()
    for company_setting in company_settings:
        company_settings_list[company_setting.setting_key] = company_setting.setting_value
    
    group_name = ''
    user_group = UserAssignedGroup.objects.filter(user=user).first()
    if user_group:
        group_name = user_group.group.name 

    company = user_branch.company
    return {
        'logged_in_time' : datetime.now().strftime('%Y-%m-%d %H:%M'),
        'token' : token,
        'user':GetFullUserSerializer(user, context={'request' : request}).data,
        'role':group_name,
        "company":{
            "id":company.id, 
            "name":company.name,
            "short_name":company.short_name,
            "logo_url":company.logo_url,
            "city":company.city,
            "address":'',
            "phone_number":company.telephone
        },
        "branch":{
            "id":user_branch.id,
            "name":user_branch.name, 
            "short_name":user_branch.short_name,
            "address":user_branch.address
        },
        "company_settings":company_settings_list,
        "permissions":UserPermissionsSerializer(UserPermissions.objects.filter(user_id=user.id,is_feature_active=True,is_company_comp_active=True,is_group_active=True,is_role_component_active=True,is_assigned_group_active=True).all(), many=True).data, 
        "profile_url":None #user.user_staff.profile_url
    }

def get_current_user(request, session_key = None, default=None):
    user_id = request.user.id
    user_session = None
    data = {"user__id": user_id}
    if request.META.get('HTTP_AUTHORIZATION', None):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]        
        data['session_token'] = token

    user_session = UserSession.objects.filter(**data).first()

    if session_key and user_session:
        if session_key in user_session.data:
            for key, value in user_session.data.items():
                if key == session_key:
                    return value
        else:
            return default if default else 0

    if not user_session and default:
         return default

    return user_session.data if user_session else {}

def get_logged_in_user_key():
    global logged_in_user_key
    return logged_in_user_key

def set_logged_in_user_key(new_key):
    global logged_in_user_key
    logged_in_user_key = new_key

def jwt_switched_session_response_handler(token, user):
    
    user_session = UserSession.objects.filter(user=user, session_token = token).first()
    company_id = user.user_branch.company.id
    branch_id = user.user_branch.id
    if not user_session:
        UserSession.objects.create(user=user, session_token = token, data={"company_id":company_id, "branch_id":branch_id})
    else:
        user_session.data = {"company_id":company_id, "branch_id":branch_id}
        user_session.save()

    company_settings_list = {}
    company_settings = CompanySetting.objects.filter(company_setting=user.user_branch.company.id).all()
    for company_setting in company_settings:
        company_settings_list[company_setting.setting_key] = company_setting.setting_value
    
    group_name = ''
    user_group = UserAssignedGroup.objects.filter(user=user).first()
    if user_group:
        group_name = user_group.group.name 

    company = user.user_branch.company

    return {
        'token' : token,
        'user':GetFullUserSerializer(user).data,
        'role':group_name,
        "company":{
            "id":company.id, 
            "name":company.name,
            "short_name":company.short_name,
            "logo_url":company.logo_url,
            "city":company.city,
            "address":"",
            "phone_number":company.telephone
        },
        "branch":{
            "id":user.user_branch.id,
            "name":user.user_branch.name, 
            "short_name":user.user_branch.short_name,
            "address":user.user_branch.address
        },
        "company_settings":company_settings_list,
        "permissions":UserPermissionsSerializer(UserPermissions.objects.filter(user_id=user.id,is_feature_active=True,is_company_comp_active=True,is_group_active=True,is_role_component_active=True,is_assigned_group_active=True).all(), many=True).data, 
        "profile_url":None#user.user_staff.profile_url
    }

def generate_random_string(length=50):
    characters = string.ascii_letters + string.digits  # Combine uppercase, lowercase letters and digits
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string


