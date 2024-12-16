
from rest_framework import viewsets
from rest_framework.views import APIView
from companies.serializers import *
from .models import * 
from users.models import * 
from users.helper import * 
from rest_framework.response import Response
from kwani_api.utils import get_current_user
from rest_framework import status
from systemrights.serializers import *

# Create your views here.

class SystemRightView(APIView):
    def get(self,request, format=None):
        data = []
        modules = SystemComponent.objects.filter(parent_component=0).all()
        for module in modules:
            children = self.get_children_components(module.id)
            data.append(
                        {"id":module.id, "name":module.component,
                        "key":module.key,
                        "desc":module.component_desc,"children":children,
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
           
        return Response(data) 

    def post(self, request):
        request_data = request.data
        if request_data['action'] == 'ADD':
            component_field={
            "component":request_data['name'],
            "component_desc":request_data['desc'],
            "parent_component":request_data['parent'],
            "key":request_data['key'],
            "type":request_data['type'],
            "is_active":True}
            component = SystemComponent.objects.create(**component_field)
            if component:
                return Response({"message":"Added successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'EDIT':
            system_component           = SystemComponent.objects.get(id=request_data['id'])
            system_component.type      = request_data['type']
            system_component.component = request_data['name']
            system_component.component_desc   = request_data['desc']
            system_component.parent_component = request_data['parent']
            system_component.save()
            if system_component:
                return Response({"message":"updated successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'DELETE':
            system_component = SystemComponent.objects.get(id=request_data['id'])
            if system_component:
               system_component.is_active = False
               system_component.save()
            return Response({"message":"Right Deleted successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'ACTIVATE':
            system_component = SystemComponent.objects.get(id=request_data['id'])
            if system_component:
                system_component.is_active = request_data['status']
                system_component.save()
                if request_data['status']:
                    return Response({"message":"Right activated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Right deactivated successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def get_children_components(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                children = self.get_children_components(module.id)
                if(len(children) > 0):
                    children2 = self.get_children_components(module.id)
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.component_desc,"children":children2,
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
                if(len(children) < 1):
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.component_desc,"children":[],
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
        return data
    
class SystemComponentsView(viewsets.ModelViewSet):
    serializer_class = SystemComponentSerializer
    queryset = SystemComponent.objects.all()

class CompanyTypeComponentsView(APIView):
    def get(self, request, format=None):
        data = []
        org_type_id = request.GET.get('comp_company_type', '1')
        modules = CompanyTypeComponent.objects.filter(comp_company_type__id=org_type_id).all()
        for module in modules:
            data.append(
                {"id":module.id, "system_component":module.system_component.id,
                 "comp_company_type":module.comp_company_type.id,
                 "is_active":module.is_active})
        return Response(data) 
    
    def post(self, request):
        request_data = request.data
        system_component = SystemComponent.objects.get(id=request_data['componentid'])
        org_type         = CompanyType.objects.get(id=request_data['comp_company_type'])
        result           = CompanyTypeComponent.objects.filter(comp_company_type=org_type,system_component=system_component)
        if result:
            org_type_comp = result[0]
            org_type_comp.is_active = request_data['is_active']
            org_type_comp.save()
            if org_type_comp:
                data = self.get_children_component_ids(org_type_comp.system_component.id)
                if(len(data) > 0):
                    for id in data:
                        result  = CompanyTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=SystemComponent.objects.get(id=id))
                        if result:
                            child_component = result[0]
                            child_component.is_active = org_type_comp.is_active
                            child_component.save()
                        else:
                            org_type_comp_field={"comp_company_type":org_type,"system_component":SystemComponent.objects.get(id=id),"is_active": org_type_comp.is_active}
                            CompanyTypeComponent.objects.create(**org_type_comp_field)
                self.saveParentComponent(org_type_comp)
                return Response({"message":"updated successfully"}, status=status.HTTP_200_OK)
        else:
            org_type_comp_field={"comp_company_type":org_type,"system_component":system_component,"is_active":True}
            org_type_comp  = CompanyTypeComponent.objects.create(**org_type_comp_field)
            if org_type_comp:
                data = self.get_children_component_ids(org_type_comp.system_component.id)
                if(len(data) > 0):
                    for id in data:
                        result  = CompanyTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=SystemComponent.objects.get(id=id))
                        if result:
                            child_component = result[0]
                            child_component.is_active = org_type_comp.is_active
                            child_component.save()
                        else:
                            org_type_comp_field={"comp_company_type":org_type,"system_component":SystemComponent.objects.get(id=id),"is_active": org_type_comp.is_active}
                            CompanyTypeComponent.objects.create(**org_type_comp_field)
                self.saveParentComponent(org_type_comp)
                return Response({"message":"Added successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"error occurred"}, status=status.HTTP_400_BAD_REQUEST)
    
    def saveParentComponent(self,org_type_comp):
        if org_type_comp.system_component.parent_component > 0:
            if org_type_comp.is_active:
                result  = CompanyTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=org_type_comp.system_component.parent_component)
                if result:
                    parent_component = result[0]
                    parent_component.is_active = True
                    parent_component.save()
                    if parent_component:
                        self.saveParentComponent(parent_component)
                else:
                    org_type_comp_field={"comp_company_type":org_type_comp.comp_company_type,"system_component":SystemComponent.objects.get(id=org_type_comp.system_component.parent_component),"is_active":True}
                    parent_component = CompanyTypeComponent.objects.create(**org_type_comp_field)
                    if parent_component:
                        self.saveParentComponent(parent_component)
            if not org_type_comp.is_active:
                result  = CompanyTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=org_type_comp.system_component.parent_component)
                if result:
                    parent_component = result[0]
                    children  = CompanyTypeComponent.objects.filter(system_component__parent_component=parent_component.system_component.id,is_active=True).all()
                    if len(children) < 1:
                        parent_component.is_active = False
                        parent_component.save()
                        if parent_component:
                            self.saveParentComponent(parent_component)

    def get_children_component_ids(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                data.append(module.id)
                children_modules = self.get_children_component_ids(module.id)
                if(len(children_modules) > 0):
                    for child_module in children_modules:
                        data.append(child_module)
                        children_modules2 = self.get_children_component_ids(child_module)
                        if(len(children_modules2) > 0):
                            for child_module2 in children_modules2:
                                data.append(child_module2)
                           
        return data   

class UserGroupView(viewsets.ModelViewSet):
    serializer_class = UserGroupSerializer
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        queryset = UserGroup.objects.filter(user_group_company=company_id).order_by('-id')
        return queryset
    
    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        #Save role.
        company    = Company.objects.get(id=company_id)
        serializer.save(group_added_by=self.request.user.id, user_group_company=company,is_active =True)
        

class CompanyComponentView(APIView):
    def get(self, request, format=None):
        data = []
        companyid = request.GET.get('companyid', '1')
        modules = CompanyComponent.objects.filter(company__id=companyid).all()
        for module in modules:
            data.append(
                {"id":module.id, "system_component":module.system_component.id,
                 "company":module.company.id,
                 "is_active":module.is_active})
        return Response(data) 
        
    def post(self, request):
        request_data = request.data
        system_component   = SystemComponent.objects.get(id=request_data['componentid'])
        company            = Company.objects.get(id=request_data['companyid'])
        company_component  = CompanyComponent.objects.filter(company=company,system_component=system_component).first()
        if company_component:
            company_component.is_active = request_data['is_active']
            company_component.save()

            data = self.get_children_component_ids(company_component.system_component.id)

            if(len(data) > 0):
                for id in data:
                    result  = CompanyComponent.objects.filter(company=company,system_component=SystemComponent.objects.get(id=id))
                    if result:
                        child_component = result[0]
                        child_component.is_active = company_component.is_active
                        child_component.save()
                    else:
                        CompanyComponent.objects.create(
                            company          = company,
                            system_component = SystemComponent.objects.get(id=id),
                            is_active        = company_component.is_active,
                        )
                          
            self.saveParentComponent(company_component)
            return Response({"message":"updated successfully"}, status=status.HTTP_200_OK)
        else:
            company_component_field={"company":company,"system_component":system_component,"is_active":True}
            company_component =CompanyComponent.objects.create(**company_component_field)
            if company_component:
                data = self.get_children_component_ids(company_component.system_component.id)

                if(len(data) > 0):
                    for id in data:
                        result  = CompanyComponent.objects.filter(company=company,system_component=SystemComponent.objects.get(id=id))
                        if result:
                            child_component = result[0]
                            child_component.is_active = company_component.is_active
                            child_component.save()
                        else:
                            CompanyComponent.objects.create(
                                company    = company,
                                system_component = SystemComponent.objects.get(id=id),
                                is_active        = company_component.is_active,
                            )
                          
                self.saveParentComponent(company_component)
                return Response({"message":"Added successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"error occurred"}, status=status.HTTP_400_BAD_REQUEST)
    
    def saveParentComponent(self,company_component):
        if company_component.system_component.parent_component > 0:
            if company_component.is_active:
                result  = CompanyComponent.objects.filter(company=company_component.company,system_component=company_component.system_component.parent_component)
                if result:
                    parent_component = result[0]
                    parent_component.is_active = True
                    parent_component.save()
                    if parent_component:
                        self.saveParentComponent(parent_component)
                else:
                    company_component_field={"company":company_component.company,"system_component":SystemComponent.objects.get(id=company_component.system_component.parent_component),"is_active":True}
                    parent_component = CompanyComponent.objects.create(**company_component_field)
                    if parent_component:
                        self.saveParentComponent(parent_component)
            if not company_component.is_active:
                    result  = CompanyComponent.objects.filter(company=company_component.company,system_component=company_component.system_component.parent_component)
                    if result:
                        parent_component = result[0]
                        children  = CompanyComponent.objects.filter(company=company_component.company,system_component__parent_component=parent_component.system_component.id,is_active=True).all()
                        if len(children) < 1:
                            parent_component.is_active = False
                            parent_component.save()
                            if parent_component:
                                self.saveParentComponent(parent_component)

    def get_children_component_ids(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                data.append(module.id)
                children_modules = self.get_children_component_ids(module.id)
                if(len(children_modules) > 0):
                    for child_module_id in children_modules:
                        data.append(child_module_id)
                        children_modules2 = self.get_children_component_ids(child_module_id)
                        if(len(children_modules2) > 0):
                            for child_module_id2 in children_modules2:
                                data.append(child_module_id2)
        return data  
    
class CompanyRightsApiView(APIView):
    def get(self,request):
        data = []
        company_id = get_current_user(self.request, 'company_id', 1)
        modules = CompanyRightsView.objects.filter(company_id = company_id,parent=0,is_active = True,is_component_active = True).all()
        for module in modules:
            children = self.get_children_components(module.component_id,company_id)
            data.append(
                        {"id":module.id, "name":module.component,
                        "key":module.key,
                        "desc":module.desc,"children":children,
                        "parent_component":module.parent,"type":module.type})
        return Response(data) 

    def get_children_components(self,parent_id,company_id):
        data = []
        modules = CompanyRightsView.objects.filter(company_id = company_id,parent=parent_id,is_active = True,is_component_active = True).all()
        if(len(modules) > 0):
            for module in modules:
                children = self.get_children_components(module.component_id,company_id)
                if(len(children) > 0):
                    children2 = self.get_children_components(module.component_id,company_id)
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.desc,"children":children2,
                        "parent_component":module.parent,"type":module.type})
                if(len(children) < 1):
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.desc,"children":[],
                        "parent_component":module.parent,"type":module.type})
        return data

class GroupRightsView(APIView):
    def get(self,request):
        groupid  = self.request.query_params.get('groupid')
        queryset = RoleComponent.objects.filter(user_group__id=groupid)
        results  = RoleComponentSerializer(queryset,many=True).data
        return Response({"results":results,"count":len(results)}) 
                       
    def post(self,request):
        request_data = request.data
        groupid    = request_data.get('groupid') 
        rightid    = request_data.get('rightid') 
        is_active  = request_data.get('is_active')
        user_group = UserGroup.objects.get(id=groupid)
        right      = CompanyComponent.objects.filter(id=rightid).first()
        
        if right:
            role_component = RoleComponent.objects.filter(user_group=user_group,company_component=right).first()
            if role_component:
                role_component.is_active = is_active
                role_component.save()
            else:
                RoleComponent.objects.create(user_group=user_group,company_component=right,is_active=is_active,role_component_added_by = self.request.user.id)
                role_component = RoleComponent.objects.filter(user_group=user_group,company_component__id=rightid).first()

            if role_component:
                data = self.get_children_component_ids(role_component.company_component.system_component.id)

                if(len(data) > 0):
                    for id in data:
                        company_results  = CompanyComponent.objects.filter(company=role_component.company_component.company,system_component=SystemComponent.objects.get(id=id))
                        if company_results:
                            for company_result in company_results:
                                comp_results    = RoleComponent.objects.filter(user_group=user_group,company_component=company_result)
                                if comp_results:
                                    for comp_result in comp_results:
                                        comp_result.is_active = is_active
                                        comp_result.save()
                                else:
                                    RoleComponent.objects.create(user_group=user_group,company_component=company_result,is_active=is_active,role_component_added_by = self.request.user.id)
                self.saveParentRole(role_component) 
                return Response(RoleComponentSerializer(role_component).data) 
        return Response({}) 
    
    def saveParentRole(self,role_component):
        if role_component.company_component.system_component.parent_component > 0:
            if role_component.is_active:
                company = role_component.company_component.company
                parent_component = role_component.company_component.system_component.parent_component
                company_comps  = CompanyComponent.objects.filter(company=company,system_component=parent_component)
                if company_comps:
                    company_comp = company_comps[0]
                    result       = RoleComponent.objects.filter(user_group=role_component.user_group,company_component=company_comp)
                    if result:
                        parent_role = result[0]
                        parent_role.is_active = True
                        parent_role.save()
                        if parent_role:
                            self.saveParentRole(parent_role)
                    else:
                        role_component_field={"user_group":role_component.user_group,"role_component_added_by":self.request.user.id,"company_component":company_comp,"is_active":True}
                        parent_role = RoleComponent.objects.create(**role_component_field)
                        if parent_role:
                            self.saveParentRole(parent_role)

            if not role_component.is_active:
                company    = role_component.company_component.company
                parent_component = role_component.company_component.system_component.parent_component
                company_comps  = CompanyComponent.objects.filter(company=company,system_component=parent_component)
                if company_comps:
                    company_comp = company_comps[0]
                    result   = RoleComponent.objects.filter(user_group=role_component.user_group,company_component=company_comp)
                    if result:
                        parent_role = result[0]
                        children  = RoleComponent.objects.filter(user_group=parent_role.user_group,company_component__system_component__parent_component=parent_role.company_component.system_component.id,is_active=True).all()
                        if len(children) < 1:
                            parent_role.is_active = False
                            parent_role.save()
                            if parent_role:
                                self.saveParentRole(parent_role)

    def get_children_component_ids(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                data.append(module.id)
                children_modules = self.get_children_component_ids(module.id)
                if(len(children_modules) > 0):
                    for child_module in children_modules:
                        data.append(child_module)
                        children_modules2 = self.get_children_component_ids(child_module)
                        if(len(children_modules2) > 0):
                            for child_module2 in children_modules2:
                                data.append(child_module2)
        return data   
           
'''
 

class ComponentTypeView(APIView):
    def get(self, request, format=None):
        data = []
        org_type_id = request.GET.get('comp_company_type', '1')
        modules = CompanyTypeComponent.objects.filter(comp_company_type__id=org_type_id).all()
        for module in modules:
            data.append(
                {"id":module.id, "system_component":module.system_component.id,
                 "comp_company_type":module.comp_company_type.id,
                 "is_active":module.is_active})
        return Response(data) 
    
    def post(self, request):
        request_data = request.data
        system_component = SystemComponent.objects.get(id=request_data['componentid'])
        org_type         = CompanyType.objects.get(id=request_data['comp_company_type'])
        result           = CompanyTypeComponent.objects.filter(comp_company_type=org_type,system_component=system_component)
        if result:
            org_type_comp = result[0]
            org_type_comp.is_active = request_data['is_active']
            org_type_comp.save()
            if org_type_comp:
                data = self.get_children_component_ids(org_type_comp.system_component.id)
                if(len(data) > 0):
                    for id in data:
                        result  = CompanyTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=SystemComponent.objects.get(id=id))
                        if result:
                            child_component = result[0]
                            child_component.is_active = org_type_comp.is_active
                            child_component.save()
                        else:
                            org_type_comp_field={"comp_company_type":org_type,"system_component":SystemComponent.objects.get(id=id),"is_active": org_type_comp.is_active}
                            OrgTypeComponent.objects.create(**org_type_comp_field)
                self.saveParentComponent(org_type_comp)
                return Response({"message":"updated successfully"}, status=status.HTTP_200_OK)
        else:
            org_type_comp_field={"comp_company_type":org_type,"system_component":system_component,"is_active":True}
            org_type_comp  = OrgTypeComponent.objects.create(**org_type_comp_field)
            if org_type_comp:
                data = self.get_children_component_ids(org_type_comp.system_component.id)
                if(len(data) > 0):
                    for id in data:
                        result  = OrgTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=SystemComponent.objects.get(id=id))
                        if result:
                            child_component = result[0]
                            child_component.is_active = org_type_comp.is_active
                            child_component.save()
                        else:
                            org_type_comp_field={"comp_company_type":org_type,"system_component":SystemComponent.objects.get(id=id),"is_active": org_type_comp.is_active}
                            OrgTypeComponent.objects.create(**org_type_comp_field)
                self.saveParentComponent(org_type_comp)
                return Response({"message":"Added successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"error occurred"}, status=status.HTTP_400_BAD_REQUEST)
    
    def saveParentComponent(self,org_type_comp):
        if org_type_comp.system_component.parent_component > 0:
            if org_type_comp.is_active:
                result  = OrgTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=org_type_comp.system_component.parent_component)
                if result:
                    parent_component = result[0]
                    parent_component.is_active = True
                    parent_component.save()
                    if parent_component:
                        self.saveParentComponent(parent_component)
                else:
                    org_type_comp_field={"comp_company_type":org_type_comp.comp_company_type,"system_component":SystemComponent.objects.get(id=org_type_comp.system_component.parent_component),"is_active":True}
                    parent_component = OrgTypeComponent.objects.create(**org_type_comp_field)
                    if parent_component:
                        self.saveParentComponent(parent_component)
            if not org_type_comp.is_active:
                result  = OrgTypeComponent.objects.filter(comp_company_type=org_type_comp.comp_company_type,system_component=org_type_comp.system_component.parent_component)
                if result:
                    parent_component = result[0]
                    children  = OrgTypeComponent.objects.filter(system_component__parent_component=parent_component.system_component.id,is_active=True).all()
                    if len(children) < 1:
                        parent_component.is_active = False
                        parent_component.save()
                        if parent_component:
                            self.saveParentComponent(parent_component)

    def get_children_component_ids(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                data.append(module.id)
                children_modules = self.get_children_component_ids(module.id)
                if(len(children_modules) > 0):
                    for child_module in children_modules:
                        data.append(child_module)
                        children_modules2 = self.get_children_component_ids(child_module)
                        if(len(children_modules2) > 0):
                            for child_module2 in children_modules2:
                                data.append(child_module2)
                           
        return data   

class SystemRightView(APIView):
    def get(self,request, format=None):
        data = []
        modules = SystemComponent.objects.filter(parent_component=0).all()
        for module in modules:
            children = self.get_children_components(module.id)
            data.append(
                        {"id":module.id, "name":module.component,
                        "key":module.key,
                        "desc":module.component_desc,"children":children,
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
           
        return Response(data) 

    def post(self, request):
        request_data = request.data
        if request_data['action'] == 'ADD':
            component_field={
            "component":request_data['name'],
            "component_desc":request_data['desc'],
            "parent_component":request_data['parent'],
            "key":request_data['key'],
            "type":request_data['type'],
            "is_active":True}
            component = SystemComponent.objects.create(**component_field)
            if component:
                return Response({"message":"Added successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'EDIT':
            system_component           = SystemComponent.objects.get(id=request_data['id'])
            system_component.type      = request_data['type']
            system_component.component = request_data['name']
            system_component.component_desc   = request_data['desc']
            system_component.parent_component = request_data['parent']
            system_component.save()
            if system_component:
                return Response({"message":"updated successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'DELETE':
            system_component = SystemComponent.objects.get(id=request_data['id'])
            if system_component:
               system_component.is_active = False
               system_component.save()
            return Response({"message":"Right Deleted successfully"}, status=status.HTTP_200_OK)
        if request_data['action'] == 'ACTIVATE':
            system_component = SystemComponent.objects.get(id=request_data['id'])
            if system_component:
                system_component.is_active = request_data['status']
                system_component.save()
                if request_data['status']:
                    return Response({"message":"Right activated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message":"Right deactivated successfully"}, status=status.HTTP_200_OK)
        return Response({"message":"error occurred"}, status=status.HTTP_400_BAD_REQUEST)

    def get_children_components(self,parent_id):
        data = []
        modules = SystemComponent.objects.filter(parent_component=parent_id).all()
        if(len(modules) > 0):
            for module in modules:
                children = self.get_children_components(module.id)
                if(len(children) > 0):
                    children2 = self.get_children_components(module.id)
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.component_desc,"children":children2,
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
                if(len(children) < 1):
                    data.append(
                        {"id":module.id, "name":module.component,
                         "key":module.key,
                        "desc":module.component_desc,"children":[],
                        "is_active":module.is_active,
                        "parent_component":module.parent_component,"type":module.type})
        return data



class CompanyTypesView(viewsets.ModelViewSet):
    serializer_class = CompanyTypeSerializer
    queryset = CompanyType.objects.all()



    def perform_create(self, serializer):
        organisationid = get_current_user(self.request, 'organisation_id', None)
        action       = self.request.data.get('action') 
        if action == 'DELETE':
            old_role_id   = self.request.data.get('id') 
            old_role      = UserGroup.objects.get(id=old_role_id)
            assignedusers = self.request.data.get('users') 
            for assigneduser in assignedusers:
                        userAssignedRole = UserGroup.objects.filter(assigned_role__id=old_role_id,user_id__id=assigneduser['userId']).first()
                        if userAssignedRole:
                           userAssignedRole.assigned_role = UserGroup.objects.get(id=assigneduser['roleId'])
                           userAssignedRole.save()
            role_users = UserAssignedRole.objects.filter(assigned_role__id=old_role_id)
            if not role_users:
                add_audit_trail(old_role.__class__.__name__,'is_active','Deleted User Role','delete_reson',old_role.role_name,old_role.role_name,self.request.user)
                old_role.delete()
        else:
            #Save role.
            features  = self.request.data.get('features') 
            role_org  = Organisation.objects.get(id=organisationid)
            user_role = serializer.save(role_added_by=self.request.user.id, role_org=role_org,is_active =True)
            #Save role features
            if user_role:
                if len(features) > 0:
                    for feature_id in features:
                        feature = OrganisationComponent.objects.get(id=feature_id)
                        role_component_field={"user_role":user_role,"role_component_added_by":self.request.user.id,"org_component":feature,"is_active":True}
                        RoleComponent.objects.create(**role_component_field)
        


class OrganisationBranchView(viewsets.ModelViewSet):
    serializer_class = OrganisationBranchSerializer
    
    def get_queryset(self):
        organisation_id = get_current_user(self.request, 'organisation_id', None)
        return OrganisationBranch.objects.filter(branch_organisation_id=organisation_id)

    def perform_create(self, serializer):
        organisation_id = get_current_user(self.request, 'organisation_id', None)
        organisation = Organisation.objects.get(pk=organisation_id)

        #Create Head Office Branch for Organisation.
        branch = serializer.save(branch_organisation=organisation, added_by=self.request.user.id)
        

    def perform_update(self, serializer):
        branch = serializer.save()
        
class OrganisationSettingView(viewsets.ModelViewSet):
    serializer_class = OrganisationSettingSerializer
   
    queryset = OrganisationSetting.objects.all()
    
    def get_queryset(self):
        organisation_id = get_current_user(self.request, 'organisation_id', None)
        setting         = self.request.query_params.get('setting',None)
        if setting:
            return OrganisationSetting.objects.filter(org_setting__id=organisation_id,setting_key=setting)
        
        return OrganisationSetting.objects.filter(org_setting__id=organisation_id)
    
    def perform_create(self, serializer):
        organisation_id = get_current_user(self.request, 'organisation_id', None)
        organisation = Organisation.objects.get(pk=organisation_id)
        serializer.save(org_setting=organisation, setting_added_by=self.request.user.id)'''


