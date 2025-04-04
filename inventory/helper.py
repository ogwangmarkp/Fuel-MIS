
from django.db.models import Sum
from .models import Stock,Order,OrderItem,Invoice
from companies.models import  CompanyBranch
from datetime import datetime

def generate_order_number(branch_id):
    branch = CompanyBranch.objects.filter(id=branch_id).first()
    order_number_prefix = ''

    if branch and branch.order_prefix:
        order_number_prefix = str(branch.order_prefix)
    
    code = Order.objects.filter(branch=branch).count()
    return f"{order_number_prefix}{code}"


def generate_invoice_number(branch_id,order_id):
    branch = CompanyBranch.objects.filter(id=branch_id).first()
    invoice_count = Invoice.objects.filter(order__id=order_id).count() + 1
    invoice_number_prefix = ''
    
    if branch and branch.invoice_prefix:
        invoice_number_prefix = str(branch.invoice_prefix)

    return f"{invoice_number_prefix}{order_id}-{invoice_count}-{datetime.now().strftime('%Y%m%d')}"


def get_stock_balance_by_product_variation(product_variation_id,branch_id):
    stock_total  = 0
    order_total  = 0
    available_stock = 0
    sell_price   = 0
    stock_filter = {}
    stock_filter = {"order_item__product_variation__id":product_variation_id,"order_item__order__status":'Processed',"order_item__order__order_type":'Purchases'}
    if branch_id:
        stock_filter['order_item__order__branch__id'] = branch_id
    stock_totals = Stock.objects.filter(**stock_filter).aggregate(total=Sum('order_item__quantity'))['total']
    stock_price = Stock.objects.filter(**stock_filter).order_by("-id").first()

    if stock_totals:
        stock_total = stock_totals
        sell_price = stock_price.sell_price
  
    order_filter = {"product_variation__id":product_variation_id,"order__status":'Processed',"order__order_type":'Sales'}
    if branch_id:
        order_filter['order__branch__id'] = branch_id
    order_totals = OrderItem.objects.filter(**order_filter).aggregate(total=Sum('quantity'))['total']
    if order_totals:
        order_total = order_totals
    available_stock = stock_total - order_total 
    
    return {"stock_total":stock_total,"order_total":order_total,"available_stock":available_stock,"sell_price":sell_price}

''' 
def get_stock_balance_by_stock(stock,branch_id):
    stock_total  = 0
    order_total  = 0
    available_stock = 0

    stock_filter = {"id":stock.id}
    if branch_id:
        stock_filter['stock_branch__id'] = branch_id
    stock_totals = Stock.objects.filter(**stock_filter).aggregate(total=Sum('quantity'))['total']
    if stock_totals:
        stock_total = stock_totals

    order_filter = {"product":stock.product,"status":'Processed'}
    if branch_id:
        order_filter['order_branch__id'] = branch_id
    order_totals = Order.objects.filter(**order_filter).aggregate(total=Sum('quantity'))['total']
    if order_totals:
        order_total = order_totals
    available_stock = stock_total - order_total
    return {"stock_total":stock_total,"order_total":order_total,"available_stock":available_stock}

    '''