from django.db import models
from django.utils import timezone
from companies.models import Company
from customers.models import Customer
from django.conf import settings

class Region(models.Model):
	regionname = models.CharField(max_length=100)

	def __str__(self):
		return self.regionname

	class Meta:
		db_table = 'public\".\"region'


class District(models.Model):
	region = models.ForeignKey('Region', on_delete=models.PROTECT, related_name='region', null=True, blank=True)
	districtname = models.CharField(max_length=100)
	hckey = models.CharField(max_length=100, null=True, blank=True)

	def __str__(self):
		return self.districtname

	class Meta:
		db_table = 'public\".\"district'

class County(models.Model):
	district = models.ForeignKey('District', on_delete=models.PROTECT, related_name='district_id', null=True, blank=True)
	countyname = models.CharField(max_length=200)

	def __str__(self):
		return self.countyname

	class Meta:
		db_table = 'public\".\"county'

class SubCounty(models.Model):
	county = models.ForeignKey('County', on_delete=models.PROTECT, related_name='county', null=True, blank=True)
	subcountyname = models.CharField(max_length=200)
	is_verified = models.BooleanField(default=True)

	def __str__(self):
		return self.subcountyname

	class Meta:
		db_table = 'public\".\"subcounty'

class Parish(models.Model):
	subcounty = models.ForeignKey('SubCounty', on_delete=models.PROTECT, related_name='subcounty', null=True, blank=True)
	parishname = models.CharField(max_length=200)
	is_verified = models.BooleanField(default=True)

	def __str__(self):
		return self.parishname

	class Meta:
		db_table = 'public\".\"parish'

class Village(models.Model):
	parish = models.ForeignKey('Parish', on_delete=models.PROTECT, related_name='parish', null=True, blank=True)
	villagename = models.CharField(max_length=200)
	is_verified = models.BooleanField(default=True)

	def __str__(self):
		return self.villagename

	class Meta:
		db_table = 'public\".\"village'

class CustomerAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer_address')
	village  = models.ForeignKey('Village', on_delete=models.CASCADE, related_name='customer_village', null=True, blank=True)
	parish   = models.BigIntegerField(null=True, blank=True)
	subcounty = models.BigIntegerField(null=True, blank=True)
	county = models.BigIntegerField(null=True, blank=True)
	district = models.BigIntegerField(null=True, blank=True)
	physical_address = models.CharField(max_length=1555, null=True, blank=True)
	region = models.CharField(max_length=150, null=True, blank=True)
	address_added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='address_added_by')
	date_added  = models.DateTimeField(default = timezone.now)
	
	def __str__(self):
		return str(self.id)
    
	class Meta:
		unique_together = ('village', 'customer')
		db_table = 'public\".\"customer_address'

class CompanyAddress(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='company_address')
	village  = models.ForeignKey('Village', on_delete=models.CASCADE, related_name='company_village', null=True, blank=True)
	parish   = models.BigIntegerField(null=True, blank=True)
	subcounty = models.BigIntegerField(null=True, blank=True)
	county = models.BigIntegerField(null=True, blank=True)
	district = models.BigIntegerField(null=True, blank=True)
	physical_address = models.CharField(max_length=1555, null=True, blank=True)
	region = models.CharField(max_length=150, null=True, blank=True)
	address_added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='company_address_added_by')
	date_added  = models.DateTimeField(default = timezone.now)
	
	def __str__(self):
		return str(self.id)
    
	class Meta:
		unique_together = ('village', 'company')
		db_table = 'public\".\"company_address'


class LocationView(models.Model):
	id = models.IntegerField(primary_key=True)
	villagename = models.CharField(max_length=100)
	parishid = models.IntegerField()
	parishname = models.CharField(max_length=100)
	subcountyid = models.IntegerField()
	subcountyname = models.CharField(max_length=100)
	countyid = models.IntegerField()
	countyname = models.CharField(max_length=100)
	districtid = models.IntegerField()
	districtname = models.CharField(max_length=100)
	hckey = models.CharField(max_length=100)
	regionid = models.IntegerField()
	regionname = models.CharField(max_length=100)
	
	class Meta:
		managed = False
		db_table = "public\".\"location_view"
