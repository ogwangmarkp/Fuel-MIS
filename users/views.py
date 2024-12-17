
from django.shortcuts import render
from django.contrib.auth import logout, get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from users.serializers import *
from rest_framework import viewsets
from rest_framework.views import APIView
from users.models import *
from users.helper import *
from companies.models import *
# from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status
from kwani_api.utils import get_current_user, get_logged_in_user_key, generate_random_string, custom_jwt_response_handler
from django.db.models import Q
from rest_framework.permissions import AllowAny
from .permissions import *


class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        staffid = self.request.query_params.get('staffid',None)
        branch = self.request.query_params.get('branch',None)

        if staffid:
            queryset = User.objects.filter(
                user_branch__id=staffid).order_by('first_name')
        else:
            filter_query = {}
            filter_query["user_branch__company__id"] = company_id
            if branch:
                filter_query["user_branch__id"] = branch
            queryset = User.objects.filter(**filter_query).order_by('first_name')
        return queryset

    def perform_create(self, serializer):
        branch_id = self.request.data.get('user_branch')
        group_id = self.request.data.get('group')

        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', 1)

        branch = CompanyBranch.objects.get(id=branch_id)
        saved_user = serializer.save(user_branch=branch, user_added_by=self.request.user.id)
        if saved_user:
            user_assigned_group = UserAssignedGroup.objects.filter(user=saved_user).first()
            user_group = UserGroup.objects.filter(id=group_id).first()
            if user_assigned_group:
              user_assigned_group.is_active= True
              user_assigned_group.group = user_group
              user_assigned_group.save()
            else:
                user_assigned_group_field = {
                    "group": user_group, "assigned_by": self.request.user, "user": saved_user, "is_active": True}
                UserAssignedGroup.objects.create(**user_assigned_group_field)

    def perform_update(self, serializer):
        branchid = self.request.data.get('user_branch')
        group_id = self.request.data.get('group')
        updated_user = serializer.save(user_branch_id=branchid,
                        user_added_by=self.request.user.id)
        if updated_user:
            user_assigned_group = UserAssignedGroup.objects.filter(user=updated_user).first()
            user_group = UserGroup.objects.filter(id=group_id).first()
            if user_assigned_group:
              user_assigned_group.is_active= True
              user_assigned_group.group = user_group
              user_assigned_group.save()
            else:
                user_assigned_group_field = {
                    "group": user_group, "assigned_by": self.request.user, "user": updated_user, "is_active": True}
                UserAssignedGroup.objects.create(**user_assigned_group_field)


class UserView2(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        staffid = self.request.query_params.get('staffid')
        if staffid:
            queryset = User.objects.filter(
                user_branch__id=staffid).order_by('first_name')
        else:
            queryset = User.objects.filter(
                user_branch__company__id=company_id).all().order_by('first_name')
        return queryset

    def perform_create(self, serializer):
        branch_id = self.request.data.get('user_branch')
        company_id = get_current_user(self.request, 'company_id', 1)

        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', 1)

        branch = CompanyBranch.objects.get(id=branch_id)
        company = Company.objects.get(id=company_id)
        saved_user = serializer.save(
            user_branch=branch, user_added_by=self.request.user.id)
        if saved_user:
            password = self.request.data.get('password')
            staff_number = self.request.data.get('staff_number')
            group_id = self.request.data.get('group')
            saved_user.set_password(password)
            saved_user.save()
            staff_field = {"user": saved_user,
                           "staff_number": staff_number, "company": company}
            Staff.objects.create(**staff_field)

            user_group = UserGroup.objects.get(id=group_id)
            if user_group:
                user_assigned_group_field = {
                    "group": user_group, "assigned_by": self.request.user, "user": saved_user, "is_active": True}
                UserAssignedGroup.objects.create(**user_assigned_group_field)

    def perform_update(self, serializer):
        branchid = self.request.data.get('user_branch')
        password = self.request.data.get('password')
        staff_number = self.request.data.get('staff_number')

        saved_user = serializer.save(
            user_branch_id=branchid, user_added_by=self.request.user.id)
        user_group = UserGroup.objects.get(id=self.request.data.get('group'))
        user_assigned_group = UserAssignedGroup.objects.filter(
            user=saved_user).first()

        staff = Staff.objects.filter(user=saved_user).first()
        if staff:
            staff.staff_number = staff_number
            staff.save()

        reset_password = self.request.data.get('reset_password')
        if saved_user and reset_password == True:
            saved_user.set_password(password)
            saved_user.save()

        if user_assigned_group:
            user_assigned_group.user = saved_user
            user_assigned_group.group = user_group
            user_assigned_group.assigned_by = self.request.user
            user_assigned_group.save()
        else:
            user_assigned_group_field = {
                "group": user_group, "assigned_by": self.request.user, "user": saved_user, "is_active": True}
            UserAssignedGroup.objects.create(**user_assigned_group_field)


class ContactsView(viewsets.ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        search = self.request.query_params.get('search')
        phone_number = self.request.query_params.get('phone_number')

        if phone_number:
            return User.objects.filter(phone_number=phone_number, user_branch__company__id=company_id).all().order_by('first_name')

        if search:
            return User.objects.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone_number__icontains=search), user_branch__company__id=company_id).all().order_by('first_name')
        queryset = User.objects.filter(
            user_branch__company__id=company_id).all().order_by('first_name')
        return queryset

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        branch = CompanyBranch.objects.get(id=branch_id)
        serializer.save(user_branch=branch, user_added_by=self.request.user.id)

    def perform_update(self, serializer):
        branchid = self.request.data.get('branch_id')
        serializer.save(user_branch_id=branchid,
                        user_added_by=self.request.user.id)


class RestAPIJWT(APIView):
    permission_classes = [AllowAny, IsPostOnly]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            # Generating refresh and access tokens manually
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            payload = custom_jwt_response_handler(access_token, user, request)
            return Response(payload, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class LogOutUserView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_sessions = UserSession.objects.filter(user=request.user)
        if user_sessions:
            for user_session in user_sessions:
                if user_session.session_token == get_logged_in_user_key():
                    user_session.delete()
        logout(request)
        return Response({"message": "successfully logged out"}, status=status.HTTP_200_OK)


class SMSAPIAppsView(viewsets.ModelViewSet):
    serializer_class = UserAPIAppSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        search = self.request.query_params.get('search')
        if search:
            return UserAPIApp.objects.filter(Q(app_name__icontains=search), registered_by__user_branch__company__id=company_id).all().order_by('app_name')
        queryset = UserAPIApp.objects.filter(
            registered_by__user_branch__company__id=company_id).all().order_by('app_name')
        return queryset

    def perform_create(self, serializer):
        app_key = generate_random_string(30)
        serializer.save(app_key=app_key, registered_by=self.request.user)

    def perform_update(self, serializer):
        action = self.request.data.get('action', 'update')
        if action == 'generate':
            app_key = generate_random_string(30)
            serializer.save(app_key=app_key)
        else:
            serializer.save()


class ObtainAPITokenView(APIView):
    permission_classes = [AllowAny, IsPostOnly]

    def post(self, request):
        api_key = request.data.get('api_key')
        user = None
        # Auth app
        user_api_app = UserAPIApp.objects.filter(app_key=api_key).first()
        if user_api_app:
            user = authenticate(username=user_api_app.registered_by.username,
                                password=user_api_app.registered_by.username)

        if user is not None:
            # Generate JWT manually
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            access_token = jwt_encode_handler(payload)
            UserSession.objects.create(user=user, session_token=access_token, data={
                                       "company_id": user.user_branch.company.id, "branch_id": user.user_branch.id})
            return Response({'message': 'success', 'access_token': str(access_token)}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid API key'}, status=status.HTTP_401_UNAUTHORIZED)


class DepartmentView(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        filter_list = {"branch__id": branch_id}

        return Department.objects.filter(**filter_list).order_by('name')

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', 1)
        serializer.save(branch_id=branch_id, added_by=self.request.user)


class JobTitleView(viewsets.ModelViewSet):
    serializer_class = JobTitleSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        filter_list = {"company__id": company_id}

        return JobTitle.objects.filter(**filter_list).order_by('name')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', 1)
        serializer.save(company_id=company_id, added_by=self.request.user)


class StaffView(viewsets.ModelViewSet):
    serializer_class = StaffSerializer

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', 1)
        staffid = self.request.query_params.get('staffid')
        if staffid:
            queryset = Staff.objects.filter(
                id=staffid).order_by('user__first_name')
        else:
            queryset = Staff.objects.filter(
                company__id=company_id).all().order_by('user__first_name')
        return queryset

    def perform_create(self, serializer):
        branch_id = self.request.data.get('user_branch')
        company_id = get_current_user(self.request, 'company_id', 1)

        if not branch_id:
            branch_id = get_current_user(self.request, 'branch_id', 1)

        user_field = {
            "user_added_by": self.request.user.id,
            "email": self.request.data.get('email'),
            "first_name": self.request.data.get('first_name'),
            "last_name": self.request.data.get('last_name'),
            "phone_number": self.request.data.get('phone_number'),
            "username": f"user-{self.request.data.get('phone_number')}",
            "gender": self.request.data.get('gender'),
            "user_type": "Staff",
            "profile_url": self.request.data.get('profile_url'),
            "dob": self.request.data.get('dob'),
            "nin": self.request.data.get('nin'),
            "marital_status": self.request.data.get('marital_status'),
            "user_branch_id": branch_id
        }
        saved_user = User.objects.create(**user_field)
        if saved_user:
            saved_staff = serializer.save(
                company_id=company_id, user=saved_user)
            if saved_staff:
                staff_dept_field = {
                    "assigned_by": self.request.user,
                    "department_id": self.request.data.get('department'),
                    "is_active": True,
                    "is_main": True,
                    "staff": saved_staff
                }
                StaffAssignedDepartment.objects.create(**staff_dept_field)

    def perform_update(self, serializer):
        saved_staff = serializer.save()
        if saved_staff:
            user_field = {
                "email": self.request.data.get('email'),
                "first_name": self.request.data.get('first_name'),
                "last_name": self.request.data.get('last_name'),
                "phone_number": self.request.data.get('phone_number'),
                "gender": self.request.data.get('gender'),
                "user_type": "Staff",
                "profile_url": self.request.data.get('profile_url'),
                "dob": self.request.data.get('dob'),
                "nin": self.request.data.get('nin'),
                "marital_status": self.request.data.get('marital_status')
            }

            User.objects.filter(id=saved_staff.user.id).update(**user_field)

            staff_dept_field = {
                "assigned_by": self.request.user,
                "department_id": self.request.data.get('department'),
                "is_active": True,
                "is_main": True,
            }
            StaffAssignedDepartment.objects.filter(
                staff=saved_staff.id, is_main=True).update(**staff_dept_field)


class UserVisitsAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = self.request.user.id
        if not user_id:
            user_id = None
        query_filter = {
            "visit_by__id": user_id, "date_added__date__gte": datetime.today().strftime("%Y-%m-%d")}

        company = request.data.get('company', None)
        product = request.data.get('product', None)

        if company:
            query_filter["resource_type"] = 'company'
            query_filter["resource_id"] = company
            visit_count = UserVisit.objects.filter(**query_filter).count()
            if user_id:
                if visit_count < 1:
                    UserVisit.objects.create(
                        resource_type='company',
                        resource_id=company,
                        visit_by_id=user_id
                    )
            else:
                UserVisit.objects.create(
                    resource_type='company',
                    resource_id=company,
                    visit_by_id=user_id
                )

        if product:
            query_filter["resource_type"] = 'product'
            query_filter["resource_id"] = product
            visit_count = UserVisit.objects.filter(**query_filter).count()
            if user_id:
                if visit_count < 1:
                    UserVisit.objects.create(
                        resource_type='product',
                        resource_id=product,
                        visit_by_id=user_id
                    )
            else:
                UserVisit.objects.create(
                    resource_type='product',
                    resource_id=product,
                    visit_by_id=user_id
                )

        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class UserLikesAPIView(APIView):
    def post(self, request):
        user = self.request.user
        query_filter = {"liked_by": user}
        action = request.data.get('action', None)
        company = request.data.get('company', None)
        product = request.data.get('product', None)

        if company:
            query_filter["resource_type"] = 'company'
            query_filter["resource_id"] = company
            likes = UserLike.objects.filter(**query_filter).count()

            if likes < 1 and action == 'liked':
                UserLike.objects.create(
                    resource_type='company',
                    resource_id=company,
                    liked_by=user
                )

            if likes > 0 and action == 'un-liked':
                UserLike.objects.filter(**query_filter).delete()

        if product:
            query_filter["resource_type"] = 'product'
            query_filter["resource_id"] = product
            likes = UserLike.objects.filter(**query_filter).count()

            if likes < 1 and action == 'liked':
                UserLike.objects.create(
                    resource_type='product',
                    resource_id=product,
                    liked_by=user
                )

            if likes > 0 and action == 'un-liked':
                UserLike.objects.filter(**query_filter).delete()
        return Response({'message': 'success'}, status=status.HTTP_200_OK)


class RegisterUserApiView(APIView):
    permission_classes = [AllowAny, IsPostOnly]

    def post(self, request, format=None):
        fullname = request.data.get('fullname')
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        telephone = request.data.get('telephone')
        user_fullname = fullname.split(" ")
        first_name = fullname
        last_name = ""
        
        if len(user_fullname) > 1:
            first_name = user_fullname[0]
            last_name =fullname.replace(first_name,"")
        user_field = {
            "email": email,
            "phone_number": telephone,
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": 'Customer'
        }
        saveUser = User.objects.create(**user_field)
        if saveUser:
            saveUser.set_password(password)
            saveUser.save()
        return Response({"message": "User successfully register", "status": "success"})
    
class ResetPasswordView(APIView):

    def get_object(self, queryset=None):
        return self.request.user
    '''
    Reset password view
    '''
    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id', None)
        new_password = request.data.get('new_password')

        if user_id:
            user = User.objects.filter(id=user_id).first()
        else:
            return Response({"message": "User with this ID does not exist."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(new_password)
        #user.pass_reset_date = timezone.now()
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)

