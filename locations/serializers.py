from rest_framework import serializers
from .models import *

class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'regionname')

    id = serializers.CharField(read_only=True)
    regionname = serializers.CharField()


class DistrictSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'districtname','region','hckey')

    id = serializers.CharField(read_only=True)
    districtname = serializers.CharField()
    hckey = serializers.CharField()
    region = serializers.CharField(source='region.regionname', read_only=True)


class CountySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = County
        fields = ('id', 'countyname','district')

    id = serializers.CharField(read_only=True)
    countyname = serializers.CharField()
    district = serializers.CharField(source='district.districtname', read_only=True)


class SubCountySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubCounty
        fields = ('id', 'subcountyname','county')

    id = serializers.CharField(read_only=True)
    subcountyname = serializers.CharField()
    county = serializers.CharField(source='county.countyname', read_only=True)


class ParishSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Parish
        fields = ('id', 'parishname','subcounty')

    id = serializers.CharField(read_only=True)
    parishname = serializers.CharField()
    subcounty = serializers.CharField(source='subcounty.subcountyname', read_only=True)


class VillageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Village
        fields = ('id', 'villagename','parish')

    id = serializers.CharField(read_only=True)
    villagename = serializers.CharField()
    parish = serializers.CharField(source='parish.parishname', read_only=True)


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = '__all__'

    id                     = serializers.CharField(read_only=True)
    date_added             = serializers.CharField(read_only=True)
    address_added_by       = serializers.CharField(read_only=True)
    customer_village_id  = serializers.CharField(read_only=True, source="village.id")
    customer_village_name  = serializers.CharField(read_only=True, source="village.villagename")
    customer_parish_id     = serializers.SerializerMethodField(read_only=True)
    customer_parishname    = serializers.SerializerMethodField(read_only=True)
    customer_subcounty_id  = serializers.SerializerMethodField(read_only=True)
    customer_subcountyname = serializers.SerializerMethodField(read_only=True)
    customer_county_id     = serializers.SerializerMethodField(read_only=True)
    customer_countyname    = serializers.SerializerMethodField(read_only=True)
    customer_district_id   = serializers.SerializerMethodField(read_only=True)
    customer_districtname  = serializers.SerializerMethodField(read_only=True)
    customer_regionname    = serializers.CharField(read_only=True, source="village.parish.subcounty.county.district.region.regionname") 

    def get_customer_district_id(self, address):
        if address.village:
            return address.village.parish.subcounty.county.district.id
        return address.district

    def get_customer_districtname(self, address):
        districtname = ''
        if address.village:
            return address.village.parish.subcounty.county.district.districtname
        else:
            if address.district:
                districtname = District.objects.get(pk=address.district).districtname
        return districtname

    def get_customer_county_id(self, address):
        if address.village:
            return address.village.parish.subcounty.county.id
        return address.county

    def get_customer_countyname(self, address):
        countyname = ''
        if address.village:
            return address.village.parish.subcounty.county.countyname
        else:
            if address.county:
                countyname = County.objects.get(pk=address.county).countyname
        return countyname
    
    def get_customer_subcounty_id(self, address):
        if address.village:
            return address.village.parish.subcounty.id
        return address.subcounty
    
    def get_customer_subcountyname(self, address):
        subcountyname = ''
        if address.village:
            return address.village.parish.subcounty.subcountyname
        else:
            if address.subcounty:
                subcountyname = SubCounty.objects.get(pk=address.subcounty).subcountyname
        return subcountyname

    def get_customer_parish_id(self, address):
        if address.village:
            return address.village.parish.id
        return address.parish

    def get_customer_parishname(self, address):
        parishname = ''
        if address.village:
            return address.village.parish.parishname
        else:
            if address.parish:
                parishname = Parish.objects.get(pk=address.parish).parishname
        return parishname

class CompanyAddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompanyAddress
        fields = '__all__'

    id                     = serializers.CharField(read_only=True)
    date_added             = serializers.CharField(read_only=True)
    address_added_by       = serializers.CharField(read_only=True)
    company_village_id  = serializers.CharField(read_only=True, source="village.id")
    company_village_name  = serializers.CharField(read_only=True, source="village.villagename")
    company_parish_id     = serializers.SerializerMethodField(read_only=True)
    company_parishname    = serializers.SerializerMethodField(read_only=True)
    company_subcounty_id  = serializers.SerializerMethodField(read_only=True)
    company_subcountyname = serializers.SerializerMethodField(read_only=True)
    company_county_id     = serializers.SerializerMethodField(read_only=True)
    company_countyname    = serializers.SerializerMethodField(read_only=True)
    company_district_id   = serializers.SerializerMethodField(read_only=True)
    company_districtname  = serializers.SerializerMethodField(read_only=True)
    company_regionname    = serializers.CharField(read_only=True, source="village.parish.subcounty.county.district.region.regionname") 

    def get_company_district_id(self, address):
        if address.village:
            return address.village.parish.subcounty.county.district.id
        return address.district

    def get_company_districtname(self, address):
        districtname = ''
        if address.village:
            return address.village.parish.subcounty.county.district.districtname
        else:
            if address.district:
                districtname = District.objects.get(pk=address.district).districtname
        return districtname

    def get_company_county_id(self, address):
        if address.village:
            return address.village.parish.subcounty.county.id
        return address.county

    def get_company_countyname(self, address):
        countyname = ''
        if address.village:
            return address.village.parish.subcounty.county.countyname
        else:
            if address.county:
                countyname = County.objects.get(pk=address.county).countyname
        return countyname
    
    def get_company_subcounty_id(self, address):
        if address.village:
            return address.village.parish.subcounty.id
        return address.subcounty
    
    def get_company_subcountyname(self, address):
        subcountyname = ''
        if address.village:
            return address.village.parish.subcounty.subcountyname
        else:
            if address.subcounty:
                subcountyname = SubCounty.objects.get(pk=address.subcounty).subcountyname
        return subcountyname

    def get_company_parish_id(self, address):
        if address.village:
            return address.village.parish.id
        return address.parish

    def get_company_parishname(self, address):
        parishname = ''
        if address.village:
            return address.village.parish.parishname
        else:
            if address.parish:
                parishname = Parish.objects.get(pk=address.parish).parishname
        return parishname
    
    
class LocationViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationView
        fields = '__all__'

    id = serializers.CharField(read_only=True)
