from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company


class ServiceCategory(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    parent = models.ForeignKey('ServiceCategory', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='serv_cat_parent')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='serv_cat_company')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='serv_cat_addedby')

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'public\".\"servive_category'

class ServiceTag(models.Model):
    tag_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    parent = models.ForeignKey('ServiceTag', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='serv_tag_parent')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='serv_tag_addedby')

    def __str__(self):
        return self.tag_name

    class Meta:
        db_table = 'public\".\"servive_tag'

class Service(models.Model):
    service_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE,
                                 related_name='service_category', null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='service_company')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_addedby')

   
    def __str__(self):
        return self.service_name

    class Meta:
        db_table = 'public\".\"service'

class ServiceVariation(models.Model):
    featured_image_url =  models.TextField(null=True, blank=True)
    variation_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    regular_price = models.FloatField(null=False, blank=False,default=0.0)
    unit_of_measure = models.CharField(
        max_length=255, default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    enable_back_order = models.BooleanField(default=False)
    lead_time = models.DateTimeField(null=True, blank=True)
    service = models.ForeignKey(
        Service, on_delete=models.CASCADE, related_name='sv_service')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sv_addedby')
 
    def __str__(self):
        return self.variation_name

    class Meta:
        db_table = 'public\".\"service_variation'


