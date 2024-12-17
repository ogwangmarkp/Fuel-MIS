from rest_framework import viewsets
from rest_framework.views import APIView
from companies.serializers import *
from companies.models import * 
from users.models import * 
from users.helper import * 
from systemrights.models import *
from systemrights.models import *
from rest_framework.response import Response
from kwani_api.utils import get_current_user
from rest_framework import status
from ledgers.helper import populate_system_coa
# Create your views here.


class CompanyTypesView(viewsets.ModelViewSet):
    serializer_class = CompanyTypeSerializer
    queryset = CompanyType.objects.all().order_by('-id')

class ServiceClassView(viewsets.ModelViewSet):
    serializer_class = ServiceClassSerializer
    queryset = ServiceClass.objects.all().order_by('-id')

class CompanyServiceClassView(viewsets.ModelViewSet):
    serializer_class = CompanyServiceClassSerializer
    
    def get_queryset(self):
        company_id = self.request.query_params.get('companyid',None)
        if company_id:
            return CompanyServiceClass.objects.filter(company__id=company_id)
        return CompanyServiceClass.objects.all().order_by('-id')
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user.id)
        

class CompaniesView(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by('-id')

    def perform_create(self, serializer):
        company_type_id = self.request.data.get('company_type')
        company = serializer.save(added_by=self.request.user.id,company_type_id=company_type_id)
        #Create admin role
        user_group_field = {"name":"System Administrator","desc":"System Administrator","group_added_by":self.request.user.id,"user_group_company":company,"is_active":True}
        user_group      = UserGroup.objects.create(**user_group_field)
        
        #Assign new components
        components = CompanyTypeComponent.objects.filter(comp_company_type__id=company_type_id).all()
        for component in components:
            if component.is_active:
                company_component_field = {"company":company,"system_component":component.system_component,"is_active":True}
                company_component       = CompanyComponent.objects.create(**company_component_field)
                if company_component and user_group:
                    #Assign previlleges to admin user_group
                    role_component_field={"user_group":user_group,"role_component_added_by":self.request.user.id,"company_component":company_component,"is_active":True}
                    RoleComponent.objects.create(**role_component_field) 
        
        #Create Head Office for Company.
        branch = CompanyBranch(company=company, name="Head Office", short_name="HQ", status="active", added_by=self.request.user.id)
        branch.save()
        populate_system_coa(company, self.request.user.id)

    def perform_update(self, serializer):
        saved_company = serializer.save()
        populate_system_coa(saved_company, self.request.user.id)

    
class CompanyBranchView(viewsets.ModelViewSet):
    serializer_class = CompanyBranchSerializer
    
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return CompanyBranch.objects.filter(company=company_id)

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        company    = Company.objects.get(pk=company_id)
        branch     = serializer.save(company=company, added_by=self.request.user.id)
        
    def perform_update(self, serializer):
        serializer.save()


class GeneralSettingsView(APIView):

    def get(self, request, format=None):
        settings = {}
        general_settings_keys = [
            'sms_unit_cost'
        ]

        company_id = get_current_user(self.request, 'company_id', None)
        company_id = self.request.query_params.get('companyid',company_id)
        for general_settings_key in general_settings_keys:
            general_setting   = CompanySetting.objects.filter(company_setting__id=company_id,setting_key=general_settings_key).first()
            if general_setting:
                settings[general_settings_key] = general_setting.setting_value
            else:
                if general_settings_key == 'sms_unit_cost':
                    settings[general_settings_key] = ""

        return Response(settings)
    
    def post(self, request, format=None):
            company_id    = get_current_user(self.request, 'company_id', None)
            settings_data = [
                {"setting_key":"sms_unit_cost","setting_value":request.data.get('sms_unit_cost')}
            ]
            for data in settings_data:
                general_setting   = CompanySetting.objects.filter(company_setting__id=company_id,setting_key=data["setting_key"]).first()
                if general_setting:
                    general_setting.setting_key=data["setting_key"]
                    general_setting.setting_added_by=self.request.user.id
                    general_setting.setting_value = data["setting_value"]
                    general_setting.save()
                else:
                    CompanySetting.objects.create(setting_key=data["setting_key"],setting_value=data["setting_value"],company_setting=Company.objects.get(pk=company_id),setting_added_by=self.request.user.id)
            
            return Response({"message":"Success"})
      
class SwitchCompany(APIView):
    def post(self, request, format=None):
        company_id = request.data.get('company_id')
        if company_id:

            data = {"user": request.user}
            if request.META.get('HTTP_AUTHORIZATION', None):
                token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
                data['session_token'] = token

            user_session = UserSession.objects.filter(**data).first()
            if user_session:
                company = Company.objects.get(pk=company_id)
                
                company_settings_list = {}
                company_settings = CompanySetting.objects.filter(company_setting__id=company_id).all()
                for company_setting in company_settings:
                    company_settings_list[company_setting.setting_key] = company_setting.setting_value
                
                if company:
                    branch = CompanyBranch.objects.filter(company=company).first()
                    if branch:
                        branch_id = branch.id
                        user_session.data = {"company_id":company_id, "branch_id":branch_id}
                        user_session.save()
                        return Response({"message":"Switch successfully","status":"success","data":company_settings_list})
        return Response({"message":"Something went wrong","status":"failed"})

class RefreshCOAsView(APIView):
    def put(self, request, format=None):
        '''
        Update COAs.
        '''
        company_id = get_current_user(self.request, 'company_id', None)
        if company_id and request.user.is_superuser:
            populate_system_coa(Company.objects.get(pk=company_id), self.request.user.id)
            return Response({"status": "ok","message":"Charts successfully updated."}, status=status.HTTP_200_OK)
            
        return Response({"status": "failed","message":"Permission not granted."}, status=status.HTTP_403_FORBIDDEN)
