from rest_framework import serializers
from .models import *
from .helper import *
from locations.models import CompanyAddress
from customers.serializers import CustomerSerializer
from companies.serializers import CompanyAddressSerializer
from users.models import UserVisit, UserLike
from ledgers.serializers import SupplierSerializer

class ProductCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(read_only=True, source="parent.category_name")
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductTagSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(read_only=True, source="parent.tag_name")
    added_by = serializers.CharField(read_only=True)
    class Meta:
        model = ProductTag
        fields = '__all__'


class ProductAssignedTagSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True, source="product.product_name")
    tag_name = serializers.CharField(read_only=True, source="tag.tag_name")

    class Meta:
        model = ProductAssignedTag
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True,source="category.category_name")
    company = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    def get_tags(self, obj):
        all_tags = ProductAssignedTag.objects.filter(product__id=obj.id,deleted=False)
        if all_tags:
            return ProductAssignedTagSerializer(all_tags,many=True).data
        return []
    
    def get_featured_image_url(self, obj):
        product_variation = ProductVariation.objects.filter(product__id=obj.id).order_by("id").first()
        if product_variation:
            return product_variation.featured_image_url
        return None
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductVariationSerializer(serializers.ModelSerializer):
    stock_balance = serializers.SerializerMethodField()
    product_name = serializers.CharField(read_only=True,source="product.product_name")
    added_by = serializers.CharField(read_only=True)
    company_address = serializers.SerializerMethodField()
    company_contact = serializers.SerializerMethodField()

    def get_stock_balance(self, obj):
        branch_id = self.context.get('branch_id', None)
        stock_total = get_stock_balance_by_product_variation(obj.id,branch_id)
        return stock_total
    
    def get_company_address(self, obj):
        company_address = CompanyAddress.objects.filter(company__id=obj.product.company.id)
        return CompanyAddressSerializer(company_address,many=True, read_only=True).data
    
    def get_company_contact(self, obj):
        company = Company.objects.get(pk=obj.product.company.id)
        return {
            "name":company.name,
            "telephone":company.telephone,
            "email":company.email,
            "website_url":company.website_url
        }
    
    class Meta:
        model = ProductVariation
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(read_only=True,source="order_item.product_variation.product.category.category_name")
    product_name = serializers.CharField(read_only=True,source="order_item.product_variation.product.product_name")
    variation_name = serializers.CharField(read_only=True,source="order_item.product_variation.variation_name")
    description = serializers.CharField(read_only=True,source="order_item.product_variation.product.description")
    transaction = serializers.CharField(read_only=True,source="order_item.transaction.reference_no")
    quantity = serializers.CharField(read_only=True,source="order_item.quantity")
    purchase_price = serializers.CharField(read_only=True,source="order_item.price")
    branch = serializers.CharField(read_only=True,source="order_item.order.branch.name")
    added_by = serializers.CharField(read_only=True)

    '''def get_stock_balance(self, obj):
        branch_id = self.context.get('branch_id', None)
        stock_total = get_stock_balance_by_product(obj.id,branch_id)
        return stock_total '''
    
    class Meta:
        model = Stock
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True,source="product_variation.product.product_name")
    variation_name = serializers.CharField(read_only=True,source="product_variation.variation_name")
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    supplier_details = serializers.SerializerMethodField()
    order_extra_details = serializers.SerializerMethodField()

    def get_order_extra_details(self, obj):
        amount = 0
        discount = 0
        order_items = OrderItem.objects.filter(order__id=obj.id)
        items_count = len(order_items)

        if order_items:
            for order_item in order_items:
                    amount += (order_item.quantity * order_item.price)
                    discount += order_item.discount
        return {
            "amount":amount,
            "discount":discount,
            "total":amount+discount,
            "items_count":items_count,
            "items":OrderItemSerializer(order_items,many=True, read_only=True).data}

    def get_supplier_details(self, obj):
        if obj.order_type == 'Purchases':
            purchase = Purchase.objects.filter(order__id=obj.id).first()
            if purchase:
                return SupplierSerializer(purchase.supplier).data
        return {}
    
    class Meta:
        model = Order
        fields = '__all__'


class RequisitionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True,source="product_variation.product.product_name")
    variation_name = serializers.CharField(read_only=True,source="product_variation.variation_name")
    price = serializers.SerializerMethodField()

    def get_price(self, obj):
        return ""
    
    class Meta:
        model = RequisitionItem
        fields = '__all__'

class PurchaseRequisitionSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    requisition_items = serializers.SerializerMethodField()

    def get_requisition_items(self, obj):
        req_items = RequisitionItem.objects.filter(purchase_requisition=obj)
        return RequisitionItemSerializer(req_items,many=True, read_only=True).data

    class Meta:
        model = PurchaseRequisition
        fields = '__all__'


class SaleRequisitionItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(read_only=True,source="product_variation.product.product_name")
    price = serializers.CharField(read_only=True,source="product_variation.regular_price")
    variation_name = serializers.CharField(read_only=True,source="product_variation.variation_name")
    customer_name = serializers.CharField(read_only=True,source="sale_requisition.customer.name")
    telephone_1 = serializers.CharField(read_only=True,source="sale_requisition.customer.telephone_1")
    vehicle_no = serializers.CharField(read_only=True,source="sale_requisition.customer.vehchle_no")
    invoice_no = serializers.CharField(read_only=True,source="sale_requisition.invoice_no")
    price = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    def get_price(self, obj):
        if obj.sale_requisition.status != 'pending':
            return obj.price_at
        return float(obj.product_variation.regular_price)
    
    def get_discount(self, obj):
        if obj.sale_requisition.status != 'pending':
            return obj.discount_at
        return float(obj.product_variation.product.discount)
    
    class Meta:
        model = SaleRequisitionItem
        fields = '__all__'


class  SaleRequisitionSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    requisition_items = serializers.SerializerMethodField()
    requisition_totals = serializers.SerializerMethodField()
    customer_name = serializers.CharField(read_only=True,source="customer.name")
    telephone_1 = serializers.CharField(read_only=True,source="customer.telephone_1")
    vehicle_no = serializers.CharField(read_only=True,source="customer.vehchle_no")
    def get_requisition_items(self, obj):
        req_items = SaleRequisitionItem.objects.filter(sale_requisition=obj)
        return SaleRequisitionItemSerializer(req_items,many=True, read_only=True).data
    
    def get_requisition_totals(self, obj):
        qty = 0
        amount = 0
        discount = 0
        paid_amount = 0
        paid_discount = 0
        price = 0
        is_paid = False
        discount_rate = 0
        req_items = SaleRequisitionItem.objects.filter(sale_requisition=obj)
        if req_items:
            for req_item in req_items:
                if obj.status == 'pending':
                    price = float(req_item.product_variation.regular_price)
                    discount_rate = float(req_item.product_variation.product.discount)
                else:
                    price = req_item.price_at
                    discount_rate = req_item.discount_at

                qty += float(req_item.quantity)
                amount += float(req_item.quantity) * price
                discount += float(req_item.quantity) * price * discount_rate * 0.01
                order_item = OrderItem.objects.filter(order=obj.order, product_variation=req_item.product_variation).first()
                
                if order_item:
                    is_paid = True
                    paid_amount += float(order_item.quantity) * float(order_item.price)
                    paid_discount += float(order_item.discount) 
        return {"is_paid":is_paid,"qty":qty,"amount":amount,"discount":discount,"paid_amount":paid_amount,"paid_discount":paid_discount}
    
    class Meta:
        model = SaleRequisition
        fields = '__all__'

 
class PumpSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(read_only=True)
    added_by = serializers.IntegerField(read_only=True)
    branch_name = serializers.CharField(read_only=True,source='branch.name')

    class Meta:
        model = Pump
        fields = '__all__'

class PumpAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(read_only=True)
    pump_name = serializers.CharField(read_only=True,source='pump.name')
    teller = serializers.CharField(read_only=True,source='user.username')
    branch_name = serializers.CharField(read_only=True,source='pump.branch.name')
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = PumpAssignment
        fields = '__all__'

class PumpReadingSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(read_only=True)
    pump_name = serializers.CharField(read_only=True,source='pump_assignment.pump.name')
    teller = serializers.CharField(read_only=True,source='pump_assignment.user.username')
    branch_name = serializers.CharField(read_only=True,source='pump_assignment.pump.branch.name')
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = PumpReading
        fields = '__all__'

class PumpProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(read_only=True)
    pump_name = serializers.CharField(read_only=True,source='pump.name')
    product_name = serializers.CharField(read_only=True,source='product.product.product_name')
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = PumpProduct
        fields = '__all__'

class ShiftSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    date_added = serializers.DateTimeField(read_only=True)
    branch_name = serializers.CharField(read_only=True,source='branch.name')
    added_by = serializers.CharField(read_only=True)
    branch = serializers.CharField(read_only=True)

    class Meta:
        model = Shift
        fields = '__all__'



'''
class OrganisationSuppliersSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    last_updated_date = serializers.CharField(read_only=True)
    date_added = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)
    supplier_details = serializers.SerializerMethodField()

    class Meta:
        model = OrganisationSuppliers
        fields = '__all__'
    
    def get_supplier_details(self, obj):
        customer = Customer.objects.get(pk=obj.customer.id)
        return CustomerSerializer(customer).data




class OrganisationSeasonSerializer(serializers.ModelSerializer):
    organisation = serializers.CharField(read_only=True)
    added_by = serializers.CharField(read_only=True)

    class Meta:
        model = OrganisationSeason
        fields = '__all__'
'''