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
from ledgers.models import AccountsChart, LedgerTransaction, CreditorSupplies
from ledgers.helper import generate_reference_no, get_coa_by_code, generate_chart_code
from users.models import User

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
        return Product.objects.filter(**{'company__id': company_id, "deleted": False}).order_by('-id')

    def perform_create(self, serializer):
        company_id = get_current_user(self.request, 'company_id', None)
        tag_ids = self.request.data.get('tags')
        saved_product = serializer.save(
            company_id=company_id, added_by=self.request.user)
        if saved_product:
            for tag_id in tag_ids:
                ProductAssignedTag.objects.create(**{
                    "product_id": saved_product.id,
                    "tag_id": tag_id,
                    "deleted": False,
                    "added_by": self.request.user
                })

    def perform_update(self, serializer):
        tag_ids = self.request.data.get('tags')
        saved_product = serializer.save()
        if saved_product:
            all_tags_ids = ProductAssignedTag.objects.filter(
                product__id=saved_product.id).values_list('tag__id', flat=True)
            if all_tags_ids:
                assignedTags = ProductAssignedTag.objects.filter(
                    product__id=saved_product.id)
                if assignedTags:
                    for assignedTag in assignedTags:
                        assignedTag.deleted = True
                        assignedTag.save()

                for tag_id in tag_ids:
                    if tag_id in all_tags_ids:
                        saved_tag = ProductAssignedTag.objects.filter(
                            product__id=saved_product.id, tag__id=tag_id).first()
                        saved_tag.deleted = False
                        saved_tag.save()
                    else:
                        ProductAssignedTag.objects.create(**{
                            "product_id": saved_product.id,
                            "tag_id": tag_id,
                            "deleted": False,
                            "added_by": self.request.user
                        })
            else:
                for tag_id in tag_ids:
                    ProductAssignedTag.objects.create(**{
                        "product_id": saved_product.id,
                        "tag_id": tag_id,
                        "deleted": False,
                        "added_by": self.request.user
                    })


class ProductVariationsViewSet(viewsets.ModelViewSet):
    serializer_class = ProductVariationSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('variation_name','product__product_name' )

    def get_queryset(self):
        product_id = self.request.query_params.get('product', None)
        if product_id:
            return ProductVariation.objects.filter(**{'product__id': product_id, "deleted": False}).order_by('-id')
        return ProductVariation.objects.filter(**{"deleted": False}).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


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
            variation_name = f'{
                variation.product.product_name} ({variation.variation_name})'
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
        payment_method = self.request.data.get('payment_method')
        order_items = self.request.data.get('order_items')
        company_id = get_current_user(self.request, 'company_id', None)
        branch_id = get_current_user(self.request, 'branch_id', None)
        saved_order = serializer.save(
            branch_id=branch_id, added_by=self.request.user)
        
        if saved_order:
            if order_type == 'Purchases':
                supplier_id = self.request.data.get('supplier')
                credit_chart_id = self.request.data.get('credit_chart')
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
                    if status == 'Processed' and saved_item:
                        variation = ProductVariation.objects.get(
                            pk=order_item['product_variation'])
                        variation_name = variation.product.product_name
                        if len(variation.variation_name) > 0:
                            variation_name = f'{
                                variation.product.product_name} ({variation.variation_name})'
                        debit_chart = variation.product.chart_account

                        # Generate reference number
                        reference_no = generate_reference_no(
                            debit_chart.account_line, company_id, 'ast')
                        heading = 'Order Payment: ' + variation_name + \
                            " of amount: "+str(order_item['total'])

                        # Save transaction
                        transaction = LedgerTransaction(amount=float(order_item['total']), heading=heading, record_date=record_date, pay_method=payment_method,
                                                        reference_no=reference_no, debit_chart=debit_chart, credit_chart_id=credit_chart_id, branch_id=branch_id, added_by=self.request.user)
                        saved_trans = transaction.save()
                        if saved_trans:
                            saved_item.transaction = saved_trans
                            saved_item.save() 
            
            if order_type == 'Sales':
                customer_id = self.request.data.get('customer',None)
                debit_chart_id = self.request.data.get('debit_chart')                
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
                    if status == 'Processed' and saved_item:
                        variation = ProductVariation.objects.get(
                            pk=order_item['product_variation'])
                        variation_name = variation.product.product_name
                        if len(variation.variation_name) > 0:
                            variation_name = f'{
                                variation.product.product_name} ({variation.variation_name})'
                        credit_chart = variation.product.chart_account

                        # Generate reference number
                        reference_no = generate_reference_no(
                            credit_chart.account_line, company_id, 'ast')
                        heading = 'Sales Order Payment: ' + variation_name + \
                            " of amount: "+str(order_item['total'])

                        # Save transaction
                        transaction = LedgerTransaction(amount=float(order_item['total']), heading=heading, record_date=record_date, pay_method=payment_method,
                                                        reference_no=reference_no, debit_chart_id=debit_chart_id, credit_chart = credit_chart, branch_id=branch_id, added_by=self.request.user)
                        saved_trans = transaction.save()
                        if saved_trans:
                            saved_item.transaction = saved_trans
                            saved_item.save() 

   
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
        company_id = get_current_user(self.request, 'company_id', None)
        branch = self.request.query_params.get('branch',None)
        filter_query = {}
        filter_query["branch__company__id"] = company_id
        if branch:
                filter_query["branch__id"] = branch
        return Pump.objects.filter(**filter_query)

    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user.id)

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
        shifts = Shift.objects.filter(branch__id=branch_id, name='date')
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
        branch_id = get_current_user(self.request, 'branch_id', None)
        shift = self.request.query_params.get('shift', None)
        record_date = self.request.query_params.get('record_date', None)
        pump_list = []
        filter_query = {"branch__id":branch_id}
        status = 'pending'
        pumps = Pump.objects.filter(**filter_query)
        pump_reading = PumpReading.objects.filter(
            record_date__date__gte=record_date,
            record_date__date__lte=record_date,
            shift__name=shift,
            shift__branch__id=branch_id
        ).first()
        if pump_reading:
            status = pump_reading.status

        if pumps:
            for pump in pumps:
                # Retrive proucts
                products = []
                pump_products = PumpProduct.objects.filter(pump=pump)
                if pump_products:
                   for pump_product in pump_products:
                        # Retrive pump product readings
                        pump_reading_item = PumpReadingItem.objects.filter(
                            pump_product=pump_product,
                            pump_reading__record_date__date__gte=record_date,
                            pump_reading__record_date__date__lte=record_date,
                            pump_reading__shift__name=shift).first()
                        if pump_reading_item:
                            products.append({
                            "id":pump_reading_item.id,
                            "pump_reading":pump_reading_item.pump_reading.id,
                            "pump_product":pump_product.id,
                            "product_name":pump_product.product.product.product_name,
                            "name":pump_product.name,
                            "opening":pump_reading_item.opening,
                            "closing":pump_reading_item.closing,
                            "dip1":pump_reading_item.dip1,
                            "dip2":pump_reading_item.dip2,
                            "price":pump_product.product.regular_price,
                            "sales":pump_reading_item.closing - pump_reading_item.opening,
                            "amount":(pump_reading_item.closing - pump_reading_item.opening) * pump_product.product.regular_price,
                            "attendant":pump_reading_item.attendant.id,
                            })
                        else:
                            products.append({
                            "id":0,
                            "pump_reading":"",
                            "pump_product":pump_product.id,
                            "product_name":pump_product.product.product.product_name,
                            "name":pump_product.name,
                            "opening":"",
                            "closing":"",
                            "dip1":"",
                            "dip2":"",
                            "price":pump_product.product.regular_price,
                            "sales":0,
                            "amount":0,
                            "attendant":"",
                            })
                pump_list.append({"id":pump.id,"pump_name":pump.name,"products":products})
        
        return Response({"pump_list":pump_list,"status":status})
    

    def post(self, request, format=None):
            pump_list = request.data.get('pump_list', None)
            record_date = request.data.get('record_date', None)
            shift_name = request.data.get('shift', None)
            branch_id = get_current_user(self.request, 'branch_id', None)
            # Retrive pump product readings
            shift = Shift.objects.filter(
                name=shift_name,
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
                    "status":"pending",
                    "shift":shift,
                    "added_by": self.request.user
                })

            for pump in pump_list:
                for readings in pump['products']:
                    pump_reading_item = PumpReadingItem.objects.filter(id=readings['id']).first()
                    if pump_reading_item:
                        pump_reading_item.opening = readings['opening']
                        pump_reading_item.closing = readings['closing']
                        pump_reading_item.dip1 = readings['dip1']
                        pump_reading_item.dip2 = readings['dip2']
                        pump_reading_item.attendant = User.objects.filter(id=readings['attendant']).first()
                        pump_reading_item.save()
                    else:
                        PumpReadingItem.objects.create(**{
                            "pump_reading_id":pump_reading.id,
                            "pump_product_id":readings['pump_product'],
                            "attendant_id":readings['attendant'],
                            "opening": readings['opening'],
                            "closing": readings['closing'],
                            "dip1": readings['dip1'],
                            "dip2": readings['dip2'],
                            "added_by": self.request.user
                        })
                        
            return Response({"message":"success"})
  