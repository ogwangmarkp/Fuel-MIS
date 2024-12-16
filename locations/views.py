from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .models import *
from companies.models import Company,CompanyBranch
from kwani_api.utils import get_current_user

class RegionViewSet(viewsets.ModelViewSet):
    """
    List all regions, or update, delete or create a new region.
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = (OrderingFilter, )
    ordering_fields = '__all__'

class DistrictViewSet(viewsets.ModelViewSet):
    """
    List all districts, or update, delete or create a new district.
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filter_backends = (SearchFilter, OrderingFilter,DjangoFilterBackend )
    filterset_fields = ['districtname','region']
    search_fields = ('districtname', )
    ordering_fields = '__all__'

class CountyViewSet(viewsets.ModelViewSet):
    """
    List all counties, or update, delete or create a new county.
    """
    queryset = County.objects.all()
    serializer_class = CountySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend )
    filterset_fields = ['countyname']
    search_fields = ('countyname', )
    ordering_fields = '__all__'

    def get_queryset(self):
        district_id = self.request.GET.get('district_id', None)
        if district_id:
            return County.objects.filter(district__id=district_id).order_by('countyname')
        return County.objects.all().order_by('countyname')

class SubCountyViewSet(viewsets.ModelViewSet):
    """
    List all subcounties, or update, delete or create a new subcounty.
    """
    serializer_class = SubCountySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['subcountyname', ]
    search_fields = ('subcountyname', )
    ordering_fields = '__all__'

    def get_queryset(self):
        county_id = self.request.GET.get('county_id', None)
        if county_id:
            return SubCounty.objects.filter(county__id=county_id).order_by('subcountyname')
        return SubCounty.objects.all().order_by('subcountyname')

class ParishViewSet(viewsets.ModelViewSet):
    """
    List all parishes, or update, delete or create a new parish.
    """
    serializer_class = ParishSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    filterset_fields = ['parishname', ]
    search_fields = ('parishname', )
    ordering_fields = '__all__'

    def get_queryset(self):
        subcounty = self.request.GET.get('subcounty', None)
        if subcounty:
            return Parish.objects.filter(subcounty__id=subcounty).order_by('parishname')
        return Parish.objects.all().order_by('parishname')

class VillageViewSet(viewsets.ModelViewSet):
    """
    List all villages, or update, delete or create a new village.
    """
    serializer_class = VillageSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend,  )
    filterset_fields = ['villagename', 'id']
    search_fields = ('villagename', )
    ordering_fields = '__all__'

    def get_queryset(self):
        parish = self.request.GET.get('parish', None)
        if parish:
            return Village.objects.filter(parish__id=parish).order_by('villagename')
        return Village.objects.all().order_by('villagename')
    


class CustomerAddressViewSet(viewsets.ModelViewSet):
    """
    List all customer locations
    """
    queryset = CustomerAddress.objects.all().order_by('id')
    serializer_class = CustomerAddressSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend,  )
    filterset_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'

    def get_queryset(self):
        customer_id = self.request.query_params.get('customer', None) 
        if customer_id:
            return CustomerAddress.objects.filter(customer__id=customer_id)
        return CustomerAddress.objects.all()

    def perform_create(self, serializer):
        request_data  = self.request.data
        village_id    = request_data.get('village')
        villagename   = request_data.get('villagename')
        parish_id     = request_data.get('parish')
        parishname    = request_data.get('parishname')
        subcounty_id  = request_data.get('subcounty')
        subcountyname = request_data.get('subcountyname')
        county_id     = request_data.get('county')
        county_name   = request_data.get('countyname')
        district_id   = request_data.get('district')
        district_name = request_data.get('districtname')
        village = None
       
        if district_id == None and district_name:
                saved_district = District.objects.create(districtname = district_name)
                if saved_district:
                    district_id = saved_district.id

        if district_id:
                if county_id == None and county_name:
                    saved_county = County.objects.create(district=District.objects.get(pk=district_id),countyname = county_name)
                    if saved_county:
                        county_id = saved_county.id
        if county_id:
            if subcounty_id == None and subcountyname:
                saved_subcounty= SubCounty.objects.create(
                    county   = County.objects.get(pk=county_id),
                    subcountyname = subcountyname,
                    is_verified = False      
                )
                if saved_subcounty:
                    subcounty_id = saved_subcounty.id

        if parish_id == None and subcounty_id and parishname:
            saved_parish = Parish.objects.create(
                subcounty   = SubCounty.objects.get(pk=subcounty_id),
                parishname  = parishname,
                is_verified = False      
            )
            if saved_parish:
                parish_id = saved_parish.id

        if village_id == None and parish_id and villagename:
            saved_village = Village.objects.create(
                parish  = Parish.objects.get(pk=parish_id),
                villagename = villagename,
                is_verified = False     
            )
            if saved_village:
                village_id = saved_village.id

        if village_id:
            village = Village.objects.filter(id=village_id).first()
                
        serializer.save(
            village=village,
            parish=parish_id,
            subcounty = subcounty_id,
            county   = county_id,
            district = district_id,
            address_added_by = self.request.user
        )

    def perform_update(self, serializer):
        request_data  = self.request.data
        village_id    = request_data.get('village')
        villagename   = request_data.get('villagename')
        parish_id     = request_data.get('parish')
        parishname    = request_data.get('parishname')
        subcounty_id  = request_data.get('subcounty')
        subcountyname = request_data.get('subcountyname')
        county_id     = request_data.get('county')
        county_name   = request_data.get('countyname')
        district_id   = request_data.get('district')
        district_name = request_data.get('districtname')
        village = None
    
        if district_id == None and district_name:
                saved_district = District.objects.create(districtname = district_name)
                if saved_district:
                    district_id = saved_district.id

        if district_id:
                if county_id == None and county_name:
                    saved_county = County.objects.create(district=District.objects.get(pk=district_id),countyname = county_name)
                    if saved_county:
                        county_id = saved_county.id
        if county_id:
            if subcounty_id == None and subcountyname:
                saved_subcounty= SubCounty.objects.create(
                    county   = County.objects.get(pk=county_id),
                    subcountyname = subcountyname,
                    is_verified = False      
                )
                if saved_subcounty:
                    subcounty_id = saved_subcounty.id

        if parish_id == None and subcounty_id and parishname:
            saved_parish = Parish.objects.create(
                subcounty   = SubCounty.objects.get(pk=subcounty_id),
                parishname  = parishname,
                is_verified = False      
            )
            if saved_parish:
                parish_id = saved_parish.id

        if village_id == None and parish_id and villagename:
            saved_village = Village.objects.create(
                parish  = Parish.objects.get(pk=parish_id),
                villagename = villagename,
                is_verified = False     
            )
            if saved_village:
                village_id = saved_village.id

        if village_id:
            village = Village.objects.filter(id=village_id).first()

        serializer.save(
            village=village,
            parish=parish_id,
            subcounty = subcounty_id,
            county   = county_id,
            district = district_id,
            address_added_by = self.request.user
        )

class CompanyAddressViewSet(viewsets.ModelViewSet):
    """
    List all customer locations
    """
    queryset = CompanyAddress.objects.all().order_by('id')
    serializer_class = CompanyAddressSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend,  )
    filterset_fields = '__all__'
    search_fields = '__all__'
    ordering_fields = '__all__'

    def get_queryset(self):
        company_id = self.request.query_params.get('company', None) 
        if company_id:
            return CompanyAddress.objects.filter(company__id=company_id)
        return CompanyAddress.objects.all()

    def perform_create(self, serializer):
        request_data  = self.request.data
        village_id    = request_data.get('village')
        villagename   = request_data.get('villagename')
        parish_id     = request_data.get('parish')
        parishname    = request_data.get('parishname')
        subcounty_id  = request_data.get('subcounty')
        subcountyname = request_data.get('subcountyname')
        county_id     = request_data.get('county')
        county_name   = request_data.get('countyname')
        district_id   = request_data.get('district')
        district_name = request_data.get('districtname')
        village = None
       
        if district_id == None and district_name:
                saved_district = District.objects.create(districtname = district_name)
                if saved_district:
                    district_id = saved_district.id

        if district_id:
                if county_id == None and county_name:
                    saved_county = County.objects.create(district=District.objects.get(pk=district_id),countyname = county_name)
                    if saved_county:
                        county_id = saved_county.id
        if county_id:
            if subcounty_id == None and subcountyname:
                saved_subcounty= SubCounty.objects.create(
                    county   = County.objects.get(pk=county_id),
                    subcountyname = subcountyname,
                    is_verified = False      
                )
                if saved_subcounty:
                    subcounty_id = saved_subcounty.id

        if parish_id == None and subcounty_id and parishname:
            saved_parish = Parish.objects.create(
                subcounty   = SubCounty.objects.get(pk=subcounty_id),
                parishname  = parishname,
                is_verified = False      
            )
            if saved_parish:
                parish_id = saved_parish.id

        if village_id == None and parish_id and villagename:
            saved_village = Village.objects.create(
                parish  = Parish.objects.get(pk=parish_id),
                villagename = villagename,
                is_verified = False     
            )
            if saved_village:
                village_id = saved_village.id

        if village_id:
            village = Village.objects.filter(id=village_id).first()
                
        serializer.save(
            village=village,
            parish=parish_id,
            subcounty = subcounty_id,
            county   = county_id,
            district = district_id,
            address_added_by = self.request.user
        )

    def perform_update(self, serializer):
        request_data  = self.request.data
        village_id    = request_data.get('village')
        villagename   = request_data.get('villagename')
        parish_id     = request_data.get('parish')
        parishname    = request_data.get('parishname')
        subcounty_id  = request_data.get('subcounty')
        subcountyname = request_data.get('subcountyname')
        county_id     = request_data.get('county')
        county_name   = request_data.get('countyname')
        district_id   = request_data.get('district')
        district_name = request_data.get('districtname')
        village = None
    
        if district_id == None and district_name:
                saved_district = District.objects.create(districtname = district_name)
                if saved_district:
                    district_id = saved_district.id

        if district_id:
                if county_id == None and county_name:
                    saved_county = County.objects.create(district=District.objects.get(pk=district_id),countyname = county_name)
                    if saved_county:
                        county_id = saved_county.id
        if county_id:
            if subcounty_id == None and subcountyname:
                saved_subcounty= SubCounty.objects.create(
                    county   = County.objects.get(pk=county_id),
                    subcountyname = subcountyname,
                    is_verified = False      
                )
                if saved_subcounty:
                    subcounty_id = saved_subcounty.id

        if parish_id == None and subcounty_id and parishname:
            saved_parish = Parish.objects.create(
                subcounty   = SubCounty.objects.get(pk=subcounty_id),
                parishname  = parishname,
                is_verified = False      
            )
            if saved_parish:
                parish_id = saved_parish.id

        if village_id == None and parish_id and villagename:
            saved_village = Village.objects.create(
                parish  = Parish.objects.get(pk=parish_id),
                villagename = villagename,
                is_verified = False     
            )
            if saved_village:
                village_id = saved_village.id

        if village_id:
            village = Village.objects.filter(id=village_id).first()

        serializer.save(
            village=village,
            parish=parish_id,
            subcounty = subcounty_id,
            county   = county_id,
            district = district_id,
            address_added_by = self.request.user
        )
   

class LocationViewSet(viewsets.ModelViewSet):
    """
    List all location view
    """
    serializer_class = LocationViewSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend,  )
    filterset_fields = '__all__'
    search_fields = ('villagename', )
    ordering_fields = '__all__'

    def get_queryset(self):
        limit = self.request.query_params.get('limit', None) 
        if limit:
            return LocationView.objects.all()[:int(limit)]
        return LocationView.objects.all()

