from django.contrib import admin

from .models import Company, CompanyType
@admin.register(Company)
@admin.register(CompanyType)
class CompanyAdmin(admin.ModelAdmin):
    pass