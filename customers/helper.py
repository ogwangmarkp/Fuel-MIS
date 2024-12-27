from .models import *
import random

def get_customer_next_no(company_id, customer_no = None):    
    company = Company.objects.filter(id=company_id).first()
    last_customer_no = 1

    if customer_no:
        last_customer_no = customer_no
    else:
        customer = Customer.objects.filter(company=company).order_by('-customer_old_no')
        if customer:
            last_customer_no = len(customer)

  
    #num_part = int(last_customer_no[1:])
    # num_part = int(last_customer_no)
    # Increment the number
    last_customer_no += 1
    #new_number_str = f'{last_customer_no[0]}{num_part:06d}'
    # verfiy if member number already taken  --- recursively check
    is_existing = Customer.objects.filter(customer_old_no=last_customer_no,company__id=company_id).first()
    if is_existing:
        return get_customer_next_no(company_id, is_existing.customer_old_no)
    return last_customer_no


