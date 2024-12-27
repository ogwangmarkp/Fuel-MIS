from .models import *
import calendar

def generate_months_between_dates(current_start, end_date):
        months = []
        while current_start <= end_date:
            months.append(current_start)
            # Move to the next month
            next_month = current_start.month % 12 + 1
            next_year = current_start.year + (current_start.month // 12)
            current_start = current_start.replace(year=next_year, month=next_month, day=1)
        return months


def generate_salary(contracts,start_date, end_date,user):
    #Generate all the month between the selected period
    months_list = generate_months_between_dates(start_date, end_date)
    if contracts: # All running contracts
        for contract in contracts:
            print("contract",contract.user.first_name)
            if months_list:
                for month_start in months_list:
                    print("contract",contract.user.first_name)
                    _, last_day = calendar.monthrange(month_start.year, month_start.month)
                    month_end = month_start.replace(day=last_day)
                    # Check and generate monthly salary if not exists
                    salary = Salary.objects.filter(contract=contract,pay_month__date__gte=month_start,pay_month__date__lte=month_end).first()
                    if not salary:
                        Salary.objects.create(**{
                            "pay_month":month_end,
                            "basic_salary":contract.basic_salary,
                            "contract":contract,
                            "added_by":user
                        })