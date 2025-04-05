from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import *
from .serializers import *
from datetime import datetime
from rest_framework import status
import json
from django.db.models import Q
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from kwani_api.utils import get_current_user
from ledgers.models import AccountsChart, LedgerTransaction, CreditorSupplies,CashAccount, PendingExpense
from ledgers.serializers import AccountsChartSerializer
from ledgers.helper import generate_reference_no, get_transactional_charts,get_coa_by_code, generate_chart_code
from users.models import User
from django.db.models import F, Subquery, OuterRef, Sum, Count,  Case, When, Value, FloatField
from django.db.models.functions import Coalesce,Round

class ProductCategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = ProductCategorySerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('category_name', )

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return ProductCategory.objects.filter(**{'company__id': company_id, "deleted": False}).order_by('-id')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        serializer.save(company_id=company_id, added_by=self.request.user)


class ProductTagsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductTagSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('tag_name', )

    def get_queryset(self):
        return ProductTag.objects.filter(**{"deleted": False}).order_by('tag_name')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class ProductsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('product_name', )

    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return Product.objects.filter(**{'company__id': company_id, "deleted": False}).order_by('product_name')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        saved_product = serializer.save(company_id=company_id,added_by=self.request.user )
        
        if saved_product:
            saved_variation = ProductVariation.objects.create(**{
                "variation_name" : saved_product.product_name,
                "description":self.request.data.get('description'),
                "unit_of_measure":self.request.data.get('unit_of_measure'),
                "code":self.request.data.get('code'),
                "is_default":True,
                "product" : saved_product,
                "added_by":self.request.user
            })

            if saved_variation:
                ProductPricing.objects.create(**{
                    "variation" :saved_variation,
                    "regular_price" :self.request.data.get('regular_price'),
                    "added_by":self.request.user
                }) 


    def perform_update(self, serializer):
        serializer.save()

class ProductVariationsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariationSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('variation_name','product__product_name' )

    def get_queryset(self):
        query_filter = {"deleted": False}
        product_id = self.request.query_params.get('product', None)
        if product_id:
            query_filter['product__id'] = product_id

        return ProductVariation.objects.filter(**query_filter).order_by('-id')


    def perform_create(self, serializer):
        saved_variation = serializer.save(added_by=self.request.user)
        
        if saved_variation:
                ProductPricing.objects.create(**{
                    "variation" :saved_variation,
                    "regular_price" :self.request.data.get('regular_price'),
                    "added_by":self.request.user
                }) 


class ProductPricingViewSet(viewsets.ModelViewSet):
    serializer_class = ProductPricingSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('variation__variation_name','variation__product__product_name' )
   
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        status = self.request.query_params.get('status', None)
        query_filter ={ "deleted": False,"variation__product__company__id":company_id}
        if status:
            query_filter['status'] = status
        return ProductPricing.objects.filter(**query_filter).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
    
    def perform_update(self, serializer):
        status = self.request.data.get('status',None)
        saved_price = serializer.save(added_by=self.request.user)
        if saved_price:
            if status== 'approved':
                all_pricings = ProductPricing.objects.filter(variation=saved_price.variation).exclude(id=saved_price.id)
                if all_pricings:
                    for all_pricing in all_pricings:
                        all_pricing.status = 'inactive'
                        all_pricing.save()
                



class StocksViewSet(viewsets.ModelViewSet):
    serializer_class = StockSerializer

    def get_queryset(self):
        search = self.request.GET.get('search', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_array = {'order_item__order__branch__id': branch_id}
        if search:
            filter_array["order_item__product_variation.product__product_name__icontains"] = search
        return Stock.objects.filter(**filter_array).order_by('-id')

    def perform_create(self, serializer):
        supplier_id = self.request.data.get('supplier_id')
        credit_chart_id = self.request.data.get('credit_chart')
        debit_chart_id = self.request.data.get('debit_chart')
        record_date = self.request.data.get('record_date')
        payment_method = self.request.data.get('payment_method')
        quantity = self.request.data.get('quantity')
        product_variation_id = self.request.data.get('product_variation')
        purchase_price = self.request.data.get('purchase_price')
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)

        # Generate reference number
        debit_chart = AccountsChart.objects.get(pk=debit_chart_id)
        reference_no = generate_reference_no(
            debit_chart.account_line, company_id, 'ast')
        variation = ProductVariation.objects.get(pk=product_variation_id)
        variation_name = variation.product.product_name
        if len(variation.variation_name) > 0:
            variation_name = f'{variation.product.product_name} ({variation.variation_name})'
        heading = 'Stock purchase: '+variation_name+" of amount:" + \
            str(float(purchase_price) * float(quantity))

        # Save transaction
        transaction = LedgerTransaction(amount=float(purchase_price) * float(quantity), heading=heading, record_date=record_date, pay_method=payment_method,
                                        reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
        transaction.save()
        if transaction:
            serializer.save(branch_id=branch_id,
                            added_by=self.request.user, transaction=transaction)
            if payment_method == 'credit':
                creditorsupplies = CreditorSupplies(
                    creditor_id=supplier_id, reference_transaction=transaction, added_by=self.request.user.id)
                creditorsupplies.save()


class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status','order_type']

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        is_invoice = self.request.GET.get('is_invoice', False)

        filter_array = {'branch__id': branch_id}
        if is_invoice:
            return Order.objects.filter(**filter_array).exclude(invoice_no__exact='').order_by('-record_date')
        
        return Order.objects.filter(**filter_array).order_by('-record_date')

    def perform_create(self, serializer):
        status = self.request.data.get('status')
        order_type = self.request.data.get('order_type')
        record_date = self.request.data.get('record_date')
        payment_method = self.request.data.get('payment_method',None)
        order_items = self.request.data.get('order_items')
        notes = self.request.data.get('notes',None)
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        order_number = generate_order_number(branch_id)

        saved_order = serializer.save(
            branch_id=branch_id, 
            added_by=self.request.user,
            order_number=order_number
        )
        
        if saved_order:
            if order_type == 'purchases':
                PurchaseRequisition.objects.create(**{
                    "status": 'pending',
                    "notes": notes,
                    "order": saved_order
                })

                for order_item in order_items:
                    OrderItem.objects.create(**{
                        "product_variation_id":order_item['id'],
                        "quantity": order_item['quantity'],
                        "price": order_item['regular_price'],
                        "order": saved_order,
                        "added_by": self.request.user
                    })

                ''' supplier_id = self.request.data.get('supplier',None)
                credit_chart_id = self.request.data.get('credit_chart',None)
                requisition_id =  self.request.data.get('requisition',None)
                supplier = Supplier.objects.filter(chart__id=supplier_id).first()
                requisition = PurchaseRequisition.objects.filter(id=requisition_id).first()
                if requisition:
                    requisition.order = saved_order
                    requisition.status = 'closed'
                    requisition.save()

                purchase = Purchase(
                    supplier=supplier, order=saved_order, added_by=self.request.user.id)
                purchase.save() 
                
                for order_item in order_items:
                    saved_item = OrderItem.objects.create(**{
                        "product_variation_id":order_item['product_variation'],
                        "quantity": order_item['quantity'],
                        "price": order_item['price'],
                        "order": saved_order,
                        "added_by": self.request.user
                    })

                    total = float(order_item['quantity']) * float(order_item['price'])

                    if status == 'Processed' and saved_item:
                        variation = ProductVariation.objects.get(
                            pk=order_item['product_variation'])
                        variation_name = variation.product.product_name
                        if len(variation.variation_name) > 0:
                            variation_name = f'{variation.product.product_name} ({variation.variation_name})'
                        debit_chart = variation.product.chart_account

                        # Generate reference number
                        reference_no = generate_reference_no(
                            debit_chart.account_line, company_id, 'ast')
                        heading = 'Order Payment: ' + variation_name + \
                            " of amount: "+str(total)

                        # Save transaction
                        transaction = LedgerTransaction(amount=float(total), heading=heading, record_date=record_date, pay_method=payment_method,
                                                        reference_no=reference_no, debit_chart=debit_chart, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
                        saved_trans = transaction.save()
                        if saved_trans:
                            saved_item.transaction = saved_trans
                            saved_item.save()  '''
            
            '''if order_type == 'Sales':
                customer_id = self.request.data.get('customer',None)
                debit_chart_id = self.request.data.get('debit_chart',None)
                requisition_id =  self.request.data.get('requisition',None)
                is_discounted = False
                requisition = SaleRequisition.objects.filter(id=requisition_id).first()
         
                if requisition and requisition.status =='approved' and requisition.sales_type == 'discount-sales':
                    requisition.order = saved_order
                    requisition.is_closed = True
                    requisition.save() 

                # This condition is for credit based order whereby on approval,
                #  the order remains pending status i.e. waiting for payment 
                # completion and requisition is approved
                if requisition and requisition.status =='pending':
                    order_items = self.process_auto_approval(requisition,saved_order,self.request.data)

                if requisition and requisition.sales_type == 'discount-sales':
                    is_discounted = True

                sale = Sale(
                    customer_id=customer_id, order=saved_order, added_by=self.request.user.id)
                sale.save()
                
                for order_item in order_items:
                    saved_item = OrderItem.objects.create(**{
                        "product_variation_id":order_item['product_variation'],
                        "quantity": order_item['quantity'],
                        "price": order_item['price'],
                        "order": saved_order,
                        "added_by": self.request.user
                    })
                    total = float(order_item['quantity']) * float(order_item['price'])
                    discount = 0

                    if status == 'Processed' and saved_item:
                        
                        variation = ProductVariation.objects.get(
                            pk=order_item['product_variation'])
                        variation_name = variation.product.product_name

                        if not debit_chart_id:
                            debit_chart_id = variation.product.account_recievable.id

                        if is_discounted:
                            req_item = SaleRequisitionItem.objects.filter(sale_requisition=requisition,product_variation__id=order_item['product_variation']).first()
                            discount = total * float(req_item.discount_at) * 0.01

                        if len(variation.variation_name) > 0:
                            variation_name = f'{variation.product.product_name} ({variation.variation_name})'
                        credit_chart = variation.product.chart_account
                        
                        # Generate reference number
                        reference_no = generate_reference_no(
                            credit_chart.account_line, company_id, 'ast')
                        heading = 'Sales Order Payment: ' + variation_name + \
                            " of amount: "+str(total-discount)

                        # Save transaction
                        transaction = LedgerTransaction(amount=(total-discount), heading=heading, record_date=record_date, pay_method=payment_method,
                                                        reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart = credit_chart, branch_id=branch_id, added_by=self.request.user)
                        saved_trans = transaction.save()
                        if saved_trans:
                            saved_item.discount = discount
                            saved_item.transaction = saved_trans
                            saved_item.save() 
            '''
    def process_auto_approval(self,requisition,order,request_data):
        order.status = 'Pending'
        order.save()

        requisition.order = order
        requisition.invoice_no = request_data.get("invoice_no")
        requisition.approved_notes = request_data.get("approved_notes")
        requisition.approved_by = self.request.user
        requisition.approved_date = request_data.get("record_date")
        requisition.status = 'approved'
        requisition.save()

        req_items = SaleRequisitionItem.objects.filter(sale_requisition=requisition)
        if req_items:
            for req_item in req_items:
                req_item.price_at = float(req_item.product_variation.regular_price)
                req_item.discount_at = float(req_item.product_variation.product.discount)
                req_item.save()
        req_items = SaleRequisitionItem.objects.filter(sale_requisition=requisition)
        return SaleRequisitionItemSerializer(req_items,many=True, read_only=True).data
    
class PurchaseRequisitionsViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status']

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_array = {'order__branch__id': branch_id}
        return PurchaseRequisition.objects.filter(**filter_array).order_by('-id')
    
    def perform_update(self, serializer):
        serializer.save(approved_by=self.request.user)

class InvoicesViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status']

    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_array = {'order__branch__id': branch_id}
        order_type = self.request.query_params.get('order_type', None)
        
        if order_type == 'purchases':
           filter_array['order__order_type'] = order_type
        
        return Invoice.objects.filter(**filter_array).order_by('-id')
    

    def perform_create(self, serializer):
        order_id = self.request.data.get('order')
        order_items = self.request.data.get('order_items')
        supplier = self.request.data.get('supplier')
        branch_id = get_current_user(self.request, 'branch_id', None)
        invoice_number = generate_invoice_number(branch_id,order_id)
        saved_invoice = serializer.save(added_by=self.request.user,invoice_number=invoice_number)
        
        if saved_invoice:
            purchase = Purchase(supplier_id=supplier, invoice=saved_invoice)
            purchase.save() 

            if order_items:
                for order_item in order_items:
                    InvoiceItem.objects.create(**{
                        "invoice":saved_invoice,
                        "order_item_id":order_item['id']
                    })
    

    def perform_update(self, serializer):
        serializer.save(approved_by=self.request.user)


'''
class PurchaseRequisitionsViewSet(viewsets.ModelViewSet):
    serializer_class = PurchaseRequisitionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status']
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_array = {'branch__id': branch_id}
        return PurchaseRequisition.objects.filter(**filter_array).order_by('-id')

    def perform_create(self, serializer):
        request_items = self.request.data.get('request_items')
        branch_id = get_current_user(self.request, 'branch_id', None)
        requistion = serializer.save(
            branch_id=branch_id, added_by=self.request.user)
        if requistion:
            for request_item in request_items:
                RequisitionItem.objects.create(**{
                    "product_variation_id": request_item['id'],
                    "quantity": request_item['quantity'],
                    "purchase_requisition": requistion,
                    "added_by": self.request.user
                })
    
    
    def perform_update(self, serializer):
        serializer.save(approved_by=self.request.user)

class SaleRequisitionsViewSet(viewsets.ModelViewSet):
    serializer_class = SaleRequisitionSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    filterset_fields = ['status','sales_type','is_closed']
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        filter_array = {'branch__id': branch_id}
        return SaleRequisition.objects.filter(**filter_array).order_by('-id')

    def perform_create(self, serializer):
        request_items = self.request.data.get('request_items')
        branch_id = get_current_user(self.request, 'branch_id', None)
        requistion = serializer.save(
            branch_id=branch_id, added_by=self.request.user)
        if requistion:
            for request_item in request_items:
                SaleRequisitionItem.objects.create(**{
                    "product_variation_id": request_item['id'],
                    'price_at':request_item['regular_price'],
                    "quantity": request_item['quantity'],
                    "sale_requisition": requistion,
                    "added_by": self.request.user
                })
    
    
    def perform_update(self, serializer):
        status = self.request.data.get('status')
        id = self.request.data.get('id')
        saved_requistion = None
        is_closed = False

        if status == 'closed':
            req = SaleRequisition.objects.filter(id=id).first()
            status = req.status
            is_closed = True

        saved_requistion = serializer.save(approved_by=self.request.user,status=status,is_closed=is_closed)

        if status == 'rejected' or status == 'approved':
            req_items = SaleRequisitionItem.objects.filter(sale_requisition=saved_requistion)
            if req_items:
                for req_item in req_items:
                    req_item.price_at = float(req_item.product_variation.regular_price)
                    req_item.discount_at = float(req_item.product_variation.product.discount)
                    print("req_item.product_variation.product.discount",req_item.product_variation.product.discount)
                    req_item.save()
'''                   

class StockTakingView(APIView):

    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        branch_id = get_current_user(self.request, 'branch_id', None)

        filter_query = {"order__branch__id":branch_id,"is_restocked":False,"order__status":"Processed","order__order_type":"Purchases"}
        order_ids = OrderItem.objects.filter(**filter_query).values_list('order__id', flat=True)
        orders = Order.objects.filter(id__in=order_ids).order_by("-record_date")

        count      = len(orders)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        orders = paginator.paginate_queryset(orders, request)
        json_orders = OrderSerializer(orders,many=True).data
       
        return Response({"results":json_orders,"count":count})
    
    def post(self, request, format=None):
            order_items = request.data.get('order_items', None)
            message = 'failed'
            for order_item in order_items:
                saved_stock = Stock.objects.create(**{
                    "order_item_id": order_item['id'],
                    "batch_number": order_item['batch_number'],
                    "sell_price": order_item['sell_price'],
                    "added_by": self.request.user
                })

                if saved_stock:
                    message = 'success'
                    order_item_obj = OrderItem.objects.filter(id=order_item['id']).first()
                    order_item_obj.is_restocked = True
                    order_item_obj.save()
                    
            return Response({"message":message})
    
class PumpsView(viewsets.ModelViewSet):
    serializer_class = PumpSerializer
    
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return Pump.objects.filter(branch__id=branch_id)

    def perform_create(self, serializer):
        branch_id = get_current_user(self.request, 'branch_id', None)
        serializer.save(added_by=self.request.user.id,branch_id=branch_id)
    
    def perform_update(self, serializer):
        products = self.request.data.get('products',[])
        updated_pump = serializer.save()
        if updated_pump:
            old_products = PumpProduct.objects.filter(pump=updated_pump)
            if old_products:
                for old_product in old_products:
                    old_product.is_active = False 
                    old_product.save()

            for product in products:
                pump_products = PumpProduct.objects.filter(pump=updated_pump,product__id=product['id'])
                if pump_products:
                    for pump_product in pump_products:
                        pump_product.name = product['name']
                        pump_product.is_active = product['is_active'] 
                        pump_product.save()
                else:
                    PumpProduct.objects.create(**{
                       'product_id':product['id'], 
                       'name':product['name'],  
                       'is_active':product['is_active'], 
                       'pump':updated_pump,
                       'added_by': self.request.user             
                    })

            
class PumpAssignmentsView(viewsets.ModelViewSet):
    serializer_class = PumpAssignmentSerializer
    
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return PumpAssignment.objects.filter(pump__branch__company__id=company_id)

    def perform_create(self, serializer):
        saved_assignment = serializer.save(added_by=self.request.user)
        if saved_assignment:
            PumpReading.objects.create(**{
                "pump_assignment":saved_assignment,
                "dip1":self.request.data.get('dip'),
                "added_by": self.request.user
            })

class PumpProductsView(viewsets.ModelViewSet):
    serializer_class = PumpProductSerializer
    
    def get_queryset(self):
        branch_id = get_current_user(self.request, 'branch_id', None)
        return PumpProduct.objects.filter(pump__branch__id=branch_id)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)
        

class PumpReadingsView(viewsets.ModelViewSet):
    serializer_class = PumpReadingSerializer
    
    def get_queryset(self):
        company_id = get_current_user(self.request, 'company_id', None)
        return PumpReading.objects.filter(pump_assignment__pump__branch__company__id=company_id)

    def perform_create(self, serializer):
        saved_assignment = serializer.save(added_by=self.request.user)
        if saved_assignment:
            PumpReading.objects.create(**{
                "pump_assignment":saved_assignment,
                "dip1":self.request.data.get('dip'),
                "added_by": self.request.user
            })

class ShiftsView(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    

    def get_queryset(self):
        new_shifts =['Day','Night']
        branch_id = get_current_user(self.request, 'branch_id', None)
        shifts = Shift.objects.filter(branch__id=branch_id)
        if shifts:
            return shifts
        for new_shift in new_shifts:
            Shift.objects.create(**{
                "branch_id":branch_id,
                "name":new_shift,
                "added_by": self.request.user
            }) 
        
        return Shift.objects.filter(branch__id=branch_id)

    def perform_create(self, serializer):
       branch_id = get_current_user(self.request, 'branch_id', None)
       serializer.save(branch_id=branch_id,added_by=self.request.user)


class CapturePumpReadingView(APIView):

    def get(self, request):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        shift = self.request.query_params.get('shift', None)
        status = 'draft' #self.request.query_params.get('status', None)
        is_closed = False
        record_date = self.request.query_params.get('record_date', None)
        pump_list = []
        dip_list = []
        payment_list = []

        pumps = Pump.objects.filter(**{"branch__id":branch_id})
        dip_products = ProductVariation.objects.filter(**{"is_active":True,"deleted":False,"product__company__id":company_id})
        attendants = CashAccount.objects.filter(teller__user_branch__id=branch_id)
        ''' if attendants:
            for attendant in attendants:
                payment = TempCashPayment.objects.filter(
                    teller__id = attendant.teller.id,
                    record_date__date__gte=record_date,
                    record_date__date__lte=record_date,
                    shift__name__iexact=shift
                ).first()
                if payment:
                    payment_list.append({"id":payment.id,"teller_id":attendant.teller.id,"teller":f'{attendant.teller.first_name} {attendant.teller.last_name}',"amount":payment.amount})
                else:
                    payment_list.append({"id":0,"teller_id":attendant.teller.id,"teller":f'{attendant.teller.first_name} {attendant.teller.last_name}',"amount":0})
        '''
        
        if dip_products:
            for dip_product in dip_products:
                all_dip_reading_items = DipReading.objects.filter(
                    product=dip_product,
                    record_date__date__lte=record_date,
                    shift__branch__id=branch_id
                ).order_by('-id')
                
                dip_reading_item = DipReading.objects.filter(
                product=dip_product,
                record_date__date__gte=record_date,
                record_date__date__lte=record_date,
                shift__name__iexact=shift,
                shift__branch__id=branch_id
                ).order_by('id').first()
                
                if dip_reading_item:
                    dip_list.append({
                    "id":dip_reading_item.id,
                    "product_id":dip_product.id,
                    "product_name":dip_product.product.product_name,
                    "dip1":dip_reading_item.dip1,
                    "dip2":dip_reading_item.dip2,
                    "rtt":dip_reading_item.rtt,
                    "is_exists":True,
                    "count":len(all_dip_reading_items) - 1
                    })
                else:
                    # Check if initial product readings already exists
                    is_exists = False
                    dip1 = ""
                    
                    # Update the initial dip readings
                    if all_dip_reading_items:
                       dip_reading_item = all_dip_reading_items[0]
                       is_exists = True
                       dip1 = dip_reading_item.dip2

                    dip_list.append({
                        "id":0,
                        "product_id":dip_product.id,
                        "product_name":dip_product.variation_name,
                        "dip1":dip1,
                        "dip2":"",
                        "rtt":0,
                        "is_exists":is_exists,
                        "count":len(all_dip_reading_items)
                    })
                

        if pumps:
            for pump in pumps:
                # Retrive proucts
                products = []
                pump_products = PumpProduct.objects.filter(pump=pump,is_active=True)
                if pump_products:
                   for pump_product in pump_products:
                        regular_price = 0.0
                        pricing = ProductPricing.objects.filter(variation=pump_product.product,status='approved').first()
                        if pricing:
                            regular_price = pricing.regular_price

                        # All existing readings
                        all_pump_reading_items = PumpReadingItem.objects.filter(
                            pump_product=pump_product,
                            pump_reading__record_date__date__lte=record_date,
                            pump_reading__shift__branch__id=branch_id
                        ).order_by('-id')
                        # Retrive pump product readings
                        pump_reading_item = PumpReadingItem.objects.filter(
                            pump_product=pump_product,
                            pump_reading__record_date__date__gte=record_date,
                            pump_reading__record_date__date__lte=record_date,
                            pump_reading__shift__name__iexact=shift,
                            pump_reading__shift__branch__id=branch_id).first()
                        
                        if pump_reading_item:
                            closing = pump_reading_item.closing if pump_reading_item.closing else 0
                            opening = pump_reading_item.opening if pump_reading_item.opening else 0
                            
                            products.append({
                                "id":pump_reading_item.id,
                                "pump_reading":pump_reading_item.pump_reading.id,
                                "pump_product":pump_product.id,
                                "product_name":pump_product.product.variation_name,
                                "name":pump_product.name,
                                "opening":pump_reading_item.opening,
                                "closing":pump_reading_item.closing,
                                "price":regular_price,
                                "sales":closing - opening,
                                "amount":(closing - opening) * regular_price,
                                "attendant":pump_reading_item.attendant.id if pump_reading_item.attendant else '',
                                "is_exists":True,
                                "count":len(all_pump_reading_items) - 1
                            })
                        else:
                            # Check if initial product readings already exists
                            is_exists = False
                            opening = ""
                            # Update the initial dip readings
                            if all_pump_reading_items:
                                pump_reading_item = all_pump_reading_items[0]
                                is_exists = True
                                opening = pump_reading_item.closing

                            products.append({
                                "id":0,
                                "pump_reading":"",
                                "pump_product":pump_product.id,
                                "product_name":pump_product.product.product.product_name,
                                "name":pump_product.name,
                                "opening":opening,
                                "closing":"",
                                "price":regular_price,
                                "sales":0,
                                "amount":0,
                                "attendant":"",
                                "is_exists":is_exists,
                                "count":len(all_pump_reading_items)
                            })
                if len(products) > 0:
                    pump_list.append({"id":pump.id,"pump_name":pump.name,"products":products})
        
        return Response({"pump_list":pump_list,"dip_list":dip_list,"payments":payment_list,"status":status,"is_closed":is_closed})
    

    def post(self, request, format=None):
            pump_list = request.data.get('pump_list', None)
            dip_list = request.data.get('dip_list', None)
            payments = request.data.get('payments', None)
            record_date = request.data.get('record_date', None)
            shift_name = request.data.get('shift', None)
            status = request.data.get('status', None)
            branch_id = get_current_user(self.request, 'branch_id', None)
            # Retrive pump product readings
            shift = Shift.objects.filter(
                name__iexact=shift_name,
                branch__id=branch_id
            ).first()
            pump_reading = PumpReading.objects.filter(
                record_date__date__gte=record_date,
                record_date__date__lte=record_date,
                shift=shift
            ).first()

            if not pump_reading:
                pump_reading = PumpReading.objects.create(**{
                    "record_date":record_date,
                    "status":status,
                    "shift":shift,
                    "added_by": self.request.user
                })


            if  pump_reading:
                pump_reading.status = status
                pump_reading.save()

                for pump in pump_list:
                    for readings in pump['products']:
                        if readings['opening'] and readings['closing'] and readings['attendant']:
                            pump_reading_item = PumpReadingItem.objects.filter(id=readings['id']).first()
                            if pump_reading_item:
                                pump_reading_item.opening = readings['opening'] if readings['opening'] else None
                                pump_reading_item.closing = readings['closing'] if readings['closing'] else None
                                pump_reading_item.attendant = User.objects.filter(id=readings['attendant']).first()
                                pump_reading_item.save()
                            else:
                                PumpReadingItem.objects.create(**{
                                    "pump_reading_id":pump_reading.id,
                                    "pump_product_id":readings['pump_product'],
                                    "attendant_id":readings['attendant'],
                                    "opening": readings['opening'] if readings['opening'] else None,
                                    "closing": readings['closing'] if readings['closing'] else None,
                                    "added_by": self.request.user
                                })

                if dip_list:
                    for dip_item in dip_list:
                        if dip_item['dip1'] and dip_item['dip2']:
                            dip_reading_item = DipReading.objects.filter(id=dip_item['id']).first()
                            if dip_reading_item:
                                dip_reading_item.dip1 = dip_item['dip1'] if dip_item['dip1'] else None
                                dip_reading_item.dip2 = dip_item['dip2'] if dip_item['dip2'] else None
                                dip_reading_item.rtt = dip_item['rtt'] if dip_item['rtt'] else None
                                dip_reading_item.save()
                            else:
                                DipReading.objects.create(**{
                                    "product_id":dip_item['product_id'],
                                    "dip1": dip_item['dip1'] if dip_item['dip1'] else None,
                                    "dip2": dip_item['dip2'] if dip_item['dip2'] else None,
                                    "rtt": dip_item['rtt'] if dip_item['rtt'] else None,
                                    "shift":shift,
                                    "record_date":record_date,
                                    "added_by": self.request.user
                                })
                '''if payments:
                    for payment in payments:
                        payment_item = TempCashPayment.objects.filter(id=payment['id']).first()
                        if status == 'draft'  or status == 'pending' or status == 'approved':
                            if payment_item:
                                payment_item.amount = payment['amount'] if payment['amount'] else None
                                payment_item.record_date = record_date
                                payment_item.save()
                            else:
                                TempCashPayment.objects.create(**{
                                    "teller_id":payment['teller_id'],
                                    "amount": payment['amount'] if payment['amount'] else None,
                                    "shift":shift,
                                    "record_date":record_date,
                                    "added_by": self.request.user
                                })

                             if status == 'approved':
                                # Register teller cash
                                teller_account = CashAccount.objects.filter(teller__id=payment['teller_id']).first()
                                reference_no = generate_reference_no(
                                    credit_chart.account_line, company_id, 'ast')
                                heading = 'Sales Order Payment: ' + variation_name + \
                                    " of amount: "+str(total-discount)
                        
                                transaction = LedgerTransaction(
                                    amount= payment['amount'] if payment['amount'] else None,
                                    heading= f'Cash payment recieved by {teller_account.teller.first_name} {teller_account.teller.last_name}', 
                                    record_date=record_date, 
                                    pay_method='cash',
                                    reference_no=reference_no, 
                                    debit_chart=teller_account.chart, 
                                    credit_chart=credit_chart, 
                                    branch_id=branch_id, 
                                    added_by=self.request.user)
                                transaction.save() '''

            return Response({"message":"success"})


class CashTransationView(APIView):
    
    def get(self,request):
        branch_id = get_current_user(self.request, 'branch_id', None)
        record_date = self.request.GET.get('record_date', None)
        payment_list = []
        attendants = CashAccount.objects.filter(teller__user_branch__id=branch_id)
        if attendants:
            for attendant in attendants:
                payments = LedgerTransaction.objects.filter(pay_method='cash',
                debit_chart_id=attendant.chart.id, 
                record_date__date__gte=record_date,
                record_date__date__lte=record_date,
                added_by=attendant.teller.id).values('added_by').annotate(
                total=Sum(Coalesce(F('amount'),0.0))).values('total') 
                if payments:
                    payment_list.append({"id":attendant.teller.id,"user":f'{attendant.teller.first_name} {attendant.teller.last_name}',"amount":payments[0]['total'],"record_date":record_date})
                else:
                    payment_list.append({"id":attendant.teller.id,"user":f'{attendant.teller.first_name} {attendant.teller.last_name}',"amount":0,"record_date":record_date})

        return Response({"payment_list":payment_list})
    
    
    def post(self, request, format=None):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        # Cash account details
        user_id = self.request.data.get('user')
        amount = self.request.data.get('amount')
        record_date = self.request.data.get('record_date')
        user = User.objects.filter(id=user_id).first()
        product = Product.objects.filter(company__id=company_id).first()
        credit_chart = product.chart_account
        reference_no = generate_reference_no(
            credit_chart.account_line, company_id)
        teller_account = CashAccount.objects.filter(teller__id=user_id).first()
        transaction = LedgerTransaction(
            amount=amount,
            heading= f'Cash payment recieved by {teller_account.teller.first_name} {teller_account.teller.last_name}', 
            record_date=record_date, 
            pay_method='cash',
            reference_no=reference_no, 
            debit_chart=teller_account.chart, 
            credit_chart=credit_chart, 
            branch_id=branch_id, 
            added_by=user)
        transaction.save()

        data = {
            'message': 'Transaction created.',
            'status': 'success'
        }

        return Response(data, status=status.HTTP_200_OK)
    
class PumpSummaryView(APIView):

    def get(self, request):
        record_date = self.request.query_params.get('record_date', None)
        pump_list = []
        dip_data = self.get_dip_list(record_date)
        pump_list = self.get_meter_readings(record_date)
        branch_id = get_current_user(self.request, 'branch_id', None)
        company_id = get_current_user(self.request, 'company_id', None)

        dip_list = dip_data["product_list"]
        overrall_sales = dip_data["overrall_sales"]
        overall_amount = dip_data["overall_amount"]
        overall_discount = dip_data["overall_discount"]
        overall_cash = 0
        payments = TempCashPayment.objects.filter(
            teller__user_branch__id = branch_id,
            record_date__date__gte=record_date,
            record_date__date__lte=record_date
        ).values('teller__user_branch__id').annotate(
                        total=Sum(Coalesce(F('amount'),0.0))
                ).values('total')
        
        if payments:
            overall_cash = payments[0]['total']

        transactional_charts = get_transactional_charts(
                company_id, 'expenses')

        expenses = AccountsChartSerializer(
            transactional_charts,
            many=True,
            context={
                'branch_id': branch_id,
                'start_date': record_date,
                'end_date': record_date
            }
        ).data

        req_list = SaleRequisitionItem.objects.filter(**{
            'sale_requisition__branch__id': branch_id,
            'sale_requisition__sales_type': 'credit-sales',
            'sale_requisition__status__in':['approved','close'],
            'sale_requisition__approved_date__date__gte':record_date,
            'sale_requisition__approved_date__date__lte':record_date
            }).order_by('-id')
        
        debtors = SaleRequisitionItemSerializer(req_list,many=True, read_only=True).data

        return Response({
            "pump_list":pump_list,
            "dip_list":dip_list,
            "debtors":debtors,
            "expenses":expenses,
            "overrall_sales":overrall_sales,
            "overall_amount":overall_amount,
            "overall_discount": overall_discount,
            "overall_cash":overall_cash
        })

    def get_meter_readings(self, record_date):
        branch_id = get_current_user(self.request, 'branch_id', None)
        record_date = self.request.query_params.get('record_date', None)
        pump_list = []
        filter_query = {"branch__id":branch_id}
        pumps = Pump.objects.filter(**filter_query)
        if pumps:
            for pump in pumps:
                # Retrive proucts
                products = []
                pump_products = PumpProduct.objects.filter(pump=pump)
                if pump_products:
                   for pump_product in pump_products:
                        # Retrive pump product readings
                        data_dict = {
                            "id":0,
                            "pump_product":pump_product.id,
                            "product_name":pump_product.product.product.product_name,
                            "name":pump_product.name,
                            "opening":-1,
                            "closing":-1,
                            "dip1":-1,
                            "dip2":-1,
                            "price":pump_product.product.regular_price,
                            "sales":-1,
                            "amount":-1
                        }
                        pump_reading_item_1 = PumpReadingItem.objects.filter(
                        pump_product=pump_product,
                        pump_reading__record_date__date__gte=record_date,
                        pump_reading__record_date__date__lte=record_date,
                        pump_reading__status__in = ['approved','closed']).order_by('id').first()
                        
                        pump_reading_item_2 = PumpReadingItem.objects.filter(
                        pump_product=pump_product,
                        pump_reading__record_date__date__gte=record_date,
                        pump_reading__record_date__date__lte=record_date,
                        pump_reading__status__in = ['approved','closed']).order_by('-id').first()

                        if pump_reading_item_1:
                            data_dict['opening'] = pump_reading_item_1.opening
                            data_dict['closing'] = pump_reading_item_1.closing
                            data_dict['dip1'] = pump_reading_item_1.dip1
                            data_dict['dip2'] = pump_reading_item_1.dip2
                            data_dict['sales'] = pump_reading_item_1.closing - pump_reading_item_1.opening
                            data_dict['amount'] = (pump_reading_item_1.closing - pump_reading_item_1.opening) * pump_product.product.regular_price

                        if pump_reading_item_2:
                            data_dict['closing'] = pump_reading_item_2.closing
                            data_dict['dip2'] = pump_reading_item_2.dip2
                        
                        if pump_reading_item_1 and pump_reading_item_2:
                            data_dict['sales'] = pump_reading_item_2.closing - pump_reading_item_1.opening
                            data_dict['amount'] = (pump_reading_item_2.closing - pump_reading_item_1.opening) * pump_product.product.regular_price

                        products.append(data_dict)
                pump_list.append({"id":pump.id,"pump_name":pump.name,"products":products})
        return pump_list
    
    def get_dip_list(self, record_date):
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        record_date = self.request.query_params.get('record_date', None)
        product_list = []
        filter_query = {"company__id":company_id}
        products = Product.objects.filter(**filter_query)
        overrall_sales = 0
        overall_amount = 0
        overall_discount = 0

        if products:
            for product in products:
                total_sales = 0
                discount_qty = 0
                discount_price = 0
                p_qty = 0
                p_amount = 0

                data_dict = {
                    "type":"regular",
                    "regular_sales":0,
                    "regular_amount":0,
                    "product_name":product.product_name,
                    "dip1":0,
                    "dip2":0,
                    "sales":0,
                    "price":0,
                    "amount":0
                }
                discount_rate = SaleRequisitionItem.objects.filter(**{
                    'sale_requisition__branch__id': branch_id,
                    'product_variation__product':product,
                    'sale_requisition__sales_type': 'discount-sales',
                    'sale_requisition__status__in':['approved','close'],
                    'sale_requisition__approved_date__date__gte':record_date,
                    'sale_requisition__approved_date__date__lte':record_date
                    }).order_by('-id').first()
                
                discount_sales = SaleRequisitionItem.objects.filter(**{
                    'sale_requisition__branch__id': branch_id,
                    'product_variation__product':product,
                    'sale_requisition__sales_type': 'discount-sales',
                    'sale_requisition__status__in':['approved','close'],
                    'sale_requisition__approved_date__date__gte':record_date,
                    'sale_requisition__approved_date__date__lte':record_date
                    }).values('product_variation__product','sale_requisition__sales_type').annotate(
                        total=Sum(Coalesce(F('quantity'),0.0))
                ).values('total') 
                
                
                if discount_rate:
                   discount_price = discount_rate.price_at

                if discount_sales:
                   discount_qty = discount_sales[0]['total']

                dip_reading_1 = DipReading.objects.filter(
                product=product,
                record_date__date__gte=record_date,
                record_date__date__lte=record_date).order_by('id').first()
                
                dip_reading_2 = DipReading.objects.filter(
                product=product,
                record_date__date__gte=record_date,
                record_date__date__lte=record_date).order_by('-id').first()

                if dip_reading_1:
                    data_dict['dip1'] = dip_reading_1.dip1 if dip_reading_1.dip1 else 0
                    data_dict['dip2'] = dip_reading_1.dip2 if dip_reading_1.dip2 else 0

                if dip_reading_2:
                    data_dict['dip2'] = dip_reading_2.dip2  if dip_reading_2.dip2 else 0

                pump_products = PumpProduct.objects.filter(product__product=product)
                
                if pump_products:
                   for pump_product in pump_products:
                        pump_sale = 0
                        data_dict['price'] = pump_product.product.regular_price
                        pump_reading_item_1 = PumpReadingItem.objects.filter(
                        pump_product=pump_product,
                        pump_reading__record_date__date__gte=record_date,
                        pump_reading__record_date__date__lte=record_date,
                        pump_reading__status__in = ['approved','closed']).order_by('id').first()
                        
                        pump_reading_item_2 = PumpReadingItem.objects.filter(
                        pump_product=pump_product,
                        pump_reading__record_date__date__gte=record_date,
                        pump_reading__record_date__date__lte=record_date,
                        pump_reading__status__in = ['approved','closed']).order_by('-id').first()

                        if pump_reading_item_1:
                            pump_sale = pump_reading_item_1.closing - pump_reading_item_1.opening

                        if pump_reading_item_1 and pump_reading_item_2:
                            pump_sale = pump_reading_item_2.closing - pump_reading_item_1.opening

                        total_sales += pump_sale

                regular_sales = total_sales - discount_qty
                regular_sales = regular_sales if regular_sales > 0 else 0
                p_qty = regular_sales + discount_qty
                p_amount = float(regular_sales) * float(data_dict['price']) + float(discount_qty) * float(discount_price)
                overrall_sales = overrall_sales + p_qty
                overall_amount = overall_amount + p_amount
                

                data_dict['regular_sales'] = regular_sales
                data_dict['regular_amount'] = float(regular_sales) * float(data_dict['price'])
                data_dict['sales'] = total_sales
                data_dict['estimate'] = total_sales + float(data_dict['dip1'])
                data_dict['diff'] = float(data_dict['dip2']) - (total_sales + float(data_dict['dip1']))
                data_dict['amount'] = float(total_sales) * float(data_dict['price'])
                
                # Adding Regular sales
                product_list.append(data_dict)

                #Compute discount values
                discount_amount = float(discount_qty) * float(discount_price)
                if discount_amount > 0:
                    overall_discount = float(discount_qty)  + data_dict['price'] - discount_amount
                
                # Adding discount sales
                product_list.append({
                    "type":"discount",
                    "regular_sales":"",
                    "regular_amount":"",
                    "product_name":f"C.O.P {product.product_name}",
                    "dip1":0,
                    "dip2":0,
                    "sales":discount_qty,
                    "price":discount_price,
                    "amount":discount_amount
                })
                
                # Adding product totals
                product_list.append({
                    "type":"total",
                    "regular_sales":"",
                    "regular_amount":"",
                    "product_name":"Total",
                    "dip1":0,
                    "dip2":0,
                    "sales":p_qty,
                    "price":"",
                    "amount":p_amount
                })
        return {
            "product_list":product_list,
            "overrall_sales":overrall_sales,
            "overall_amount":overall_amount,
            "overall_discount":overall_discount
        }


class BranchSummaryView(APIView):
    def get(self, request):
        record_date = self.request.query_params.get('record_date', None)
        company_id = get_current_user(self.request, 'company_id', None)
        branch_list = []
        
        customer_subquery = Customer.objects.filter(branch=OuterRef('id')).values('branch').annotate(count=Count('id')).values('count')
        pending_customers_subquery = Customer.objects.filter(branch=OuterRef('id')).values('branch').annotate(count=Count('id')).values('count')
        pumps_subquery = Pump.objects.filter(branch=OuterRef('id')).values('branch').annotate(count=Count('id')).values('count')
        users_subquery = User.objects.filter(user_branch=OuterRef('id')).values('user_branch').annotate(count=Count('id')).values('count')
        exp_subquery = PendingExpense.objects.filter(branch=OuterRef('id'),status='pending').values('branch').annotate(count=Count('id')).values('count')
        branches = CompanyBranch.objects.filter(company__id=company_id).annotate(
            customers=Coalesce(Subquery(customer_subquery), Value(0)),
            pending_customers=Coalesce(Subquery(pending_customers_subquery), Value(0)), 
            pumps=Coalesce(Subquery(pumps_subquery), Value(0)),   
            users=Coalesce(Subquery(users_subquery), Value(0)), 
            pending_exp=Coalesce(Subquery(exp_subquery), Value(0)),      
        )

        for branch in branches:
            branch_list.append({
                "branch_id":branch.id,
                "branch_name":branch.name,
                "customers":branch.customers,
                "pending_customers":branch.pending_customers,
                "pumps":branch.pumps,
                "users":branch.users,
                "pending_exp":branch.pending_exp
            })
        return Response({"branch_list":branch_list})