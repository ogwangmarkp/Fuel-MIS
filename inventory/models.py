from django.db import models
from django.conf import settings
from django.utils import timezone
from companies.models import Company, CompanyBranch
from ledgers.models import LedgerTransaction, AccountsChart,Supplier
from customers.models import Customer


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    parent = models.ForeignKey('ProductCategory', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='inv_cat_parent')
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='inv_cat_company')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inv_cat_addedby')

    def __str__(self):
        return self.category_name

    class Meta:
        db_table = 'public\".\"inv_product_category'

class ProductTag(models.Model):
    tag_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    deleted = models.BooleanField(default=False)
    parent = models.ForeignKey('ProductTag', null=True, blank=True,
                               on_delete=models.CASCADE, related_name='inv_tag_parent')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inv_tag_addedby')

    def __str__(self):
        return self.tag_name

    class Meta:
        db_table = 'public\".\"inv_product_tag'

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    can_resell = models.BooleanField(default=False)
    discount = models.FloatField(default=0.0)
    deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE,
                                 related_name='inv_product_category', null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='inv_product_Company')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inv_product_addedby')
    
    parent_cat = models.ForeignKey('ProductCategory', null=True, blank=True, on_delete=models.CASCADE, related_name='inv_parent_cat')
    chart_account = models.ForeignKey(AccountsChart, on_delete=models.CASCADE, related_name='product_chart_account', null=True, blank=True)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'public\".\"inv_product'


class ProductAssignedTag(models.Model):
    deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='pas_product')
    tag = models.ForeignKey(
        ProductTag, on_delete=models.CASCADE, related_name='pas_product')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pas_addedby')


    class Meta:
        db_table = 'public\".\"product_assigned_tag'


class ProductVariation(models.Model):
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
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='pv_product')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pv_addedby')
 
    def __str__(self):
        return self.variation_name

    class Meta:
        db_table = 'public\".\"inv_product_variation'


class Order(models.Model):
    STATUSES = (
        ('Pending', 'Pending'),
        ('Failed', 'Failed'),
        ('Processed', 'Processed'),
        ('Processing', 'Processing')
    )
    ORDER_TYPES = (
        ('Purchases', 'Purchases'),
        ('Sales', 'Sales')
    )
    heading =  models.TextField(null=False, blank=False, default='Order')
    order_number = models.CharField(
        max_length=255, default='', null=True, blank=True)
    invoice_no = models.CharField(
        max_length=255, default='', null=True, blank=True)
    status = models.CharField(
        max_length=50, default='Pending', choices=STATUSES)
    discount_coupon = models.CharField(
        max_length=255, default='', null=True, blank=True) 
    order_type = models.CharField(
        max_length=50, default='Sales', choices=ORDER_TYPES)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='order_customer', null=True)
    payment_method = models.TextField(default='', null=False, blank=False)
    record_date = models.DateTimeField(default=timezone.now)
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='order_btanch')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='order_addedby', null=False, blank=False)

    class Meta:
        db_table = 'public\".\"order'


class OrderItem(models.Model):
    price = models.FloatField(null=False, blank=False)
    quantity = models.FloatField(null=False, blank=False)
    discount = models.FloatField(null=False, blank=False, default=0)
    transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE,null=True, blank=True, related_name='order_item_transaction')
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='item_order')
    is_restocked = models.BooleanField(default=False)
    product_variation = models.ForeignKey(
        ProductVariation, on_delete=models.CASCADE, related_name='order_item_product_variation')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_item_addedby')

    class Meta:
        db_table = 'public\".\"order_item'

class Purchase(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name='purchase_supplier')
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='purchase_order')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"purchase'

class Sale(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_customer')
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='sale_order')
    date_added = models.DateTimeField(default=timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'public\".\"sale'

class Stock(models.Model):
    batch_number = models.CharField(
        max_length=255, default='', null=True, blank=True)
    sell_price = models.FloatField(null=False, blank=False)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name='stock_order_item')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_addedby')

    class Meta:
        db_table = 'public\".\"inv_stock'


class PurchaseRequisition(models.Model):
    STATUSES = (
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('approved', 'Approved'),
        ('closed', 'Closed'),
    )
    heading = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    approved_notes = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50, default='pending', choices=STATUSES)
    record_date = models.DateTimeField(default=timezone.now)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True, blank=True, related_name='pr_approved_by')
    approved_date = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, blank=True, related_name='pr_order')
    branch = models.ForeignKey(
        CompanyBranch, on_delete=models.CASCADE, related_name='pr_btanch')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                 related_name='pr_addedby', null=False, blank=False)

    class Meta:
        db_table = 'public\".\"purchase_requisition'


class RequisitionItem(models.Model):
    quantity = models.FloatField(null=False, blank=False)
    product_variation = models.ForeignKey(
        ProductVariation, on_delete=models.CASCADE, related_name='ri_product_variation')
    purchase_requisition = models.ForeignKey(
        PurchaseRequisition, on_delete=models.CASCADE, related_name='ri_purchase_requisition')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ri_addedby')

    class Meta:
        db_table = 'public\".\"requisition_ttem'

class OrderPayment(models.Model):
    quantity = models.FloatField(null=False, blank=False)
    total_discount = models.FloatField(null=False, blank=False, default=0)
    total_cost = models.FloatField(null=False, blank=False)
    stock = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name='order_item_payment_stock')
    transaction = models.ForeignKey(LedgerTransaction, on_delete=models.CASCADE,
                                    related_name='order_item_payment_transaction', null=False, blank=False)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name='order_item_payment_item')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_item_payment_addedby')

    class Meta:
        db_table = 'public\".\"order_item_payment'


class Pump(models.Model):
    name =  models.CharField(max_length=255)
    date_added = models.DateTimeField(default = timezone.now)
    added_by = models.BigIntegerField(null=True, blank=True)
    status  =  models.CharField(max_length=25, null=True, blank=True)
    branch =  models.ForeignKey(CompanyBranch, on_delete=models.CASCADE, related_name='pump_branch')

    class Meta:
        db_table = 'public\".\"pump'
    
    def __str__(self):
        return self.name

class PumpProduct(models.Model):
    name = models.TextField(null=False, blank=False)
    pump =  models.ForeignKey(Pump, on_delete=models.CASCADE, related_name='pp_pump')
    product =  models.ForeignKey(ProductVariation, on_delete=models.CASCADE, related_name='pp_product')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pp_addedby')
    date_added = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'public\".\"pump_product'


class PumpAssignment(models.Model):
    pump =  models.ForeignKey(Pump, on_delete=models.CASCADE, related_name='pa_pump')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pa_user')
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pa_addedby')
    date_added = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'public\".\"pump_assignment'

class Shift(models.Model):
    name = models.CharField(
        max_length=25, default='day')
    added_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shift_addedby')
    branch =  models.ForeignKey(CompanyBranch, on_delete=models.CASCADE, related_name='shift_branch')
    date_added = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'public\".\"shift'

        
class PumpReading(models.Model):
    APPROVAL_STATUSES = (
        ('pending', 'Pending'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('reversed', 'Reversed')
    )
    added_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prd_addedby')
    shift =  models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='prd_shift')
    record_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=25, choices=APPROVAL_STATUSES, default='open')
    date_added = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'public\".\"pump_reading'

class PumpReadingItem(models.Model):
    opening = models.FloatField(null=True,blank=True)
    closing = models.FloatField(null=True,blank=True)
    dip1 = models.FloatField(null=True,blank=True)
    dip2 = models.FloatField(null=True,blank=True)
    date_added = models.DateTimeField(null=True, blank=True)
    pump_reading =  models.ForeignKey(PumpReading, on_delete=models.CASCADE, related_name='prdi_pump_reading',blank=True)
    pump_product =  models.ForeignKey(PumpProduct, on_delete=models.CASCADE, related_name='prdi_pump_product',blank=True)
    attendant  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prdi_attendant',blank=True)
    added_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prdi_addedby')
    class Meta:
        db_table = 'public\".\"pump_reading_item'


