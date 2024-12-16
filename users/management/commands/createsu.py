from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import *
from companies.models import *
from systemrights.models import *

class Command(BaseCommand):

    def handle(self, *args, **options):
        if not get_user_model().objects.filter(username="demo@2024").exists():

            # create company type
            company_type = CompanyType.objects.create(company_type="Administration")

            # create company
            company_field={"name":"Questbanker",'company_type':company_type}
            company = Company.objects.create(**company_field)

            # create company branch
            branch_field={"name":"Head office", "company":company}
            branch      = CompanyBranch.objects.create(**branch_field)

            # create staff
            user_field = {"user_branch":branch, "user_type":"Staff"}
            user = get_user_model().objects.create_superuser("demo@2024", "admin@questbanker.com", "demo@2024", **user_field)
        
        #create ROOT ADMIN role.
        if get_user_model().objects.filter(username="demo@2024").exists():
           root_admin      = get_user_model().objects.filter(username="demo@2024").first()
           if not  UserGroup.objects.filter(name = "ROOT_ADMIN").exists():
                # Create Role
                group_field={"name":"ROOT_ADMIN","desc":"ROOT_ADMIN", "is_active":True,"group_added_by":root_admin.id,"user_group_company":root_admin.user_branch.company}
                group = UserGroup.objects.create(**group_field)
                if not  UserAssignedGroup.objects.filter(user =root_admin).exists():
                    # Assign Role
                    assigned_group_field={"group":group,"user":root_admin, "is_active":True,"assigned_by":root_admin}
                    UserAssignedGroup.objects.create(**assigned_group_field)
                else:
                    root_group  = UserAssignedGroup.objects.filter(user=root_admin).first()
                    root_group.group = group
                    root_group.save()

                
           
            