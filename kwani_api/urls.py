"""kwani_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from systemrights import views as systemrights_views
from companies import views as companies_views
from users import views as user_views
from ledgers import views as ledgers_views
from customers import views as cutomer_views
from reports import views as report_views
from inventory import views as inventory_views
from finance import views as finance_views
from locations import views as location_views
from  pos import views as pos_views
from services import views as service_views
from humanresource import views as hr_views
router = DefaultRouter() 


router.register(r'company-types', companies_views.CompanyTypesView, basename='CompanyTypes')
router.register(r'companies', companies_views.CompaniesView, basename='companies')
router.register(r'service-class', companies_views.ServiceClassView, basename='service-class')
router.register(r'company-service-class', companies_views.CompanyServiceClassView, basename='company-service-class')


router.register(r'customer-types', cutomer_views.CompanyTypesView, basename='customer-types')
router.register(r'customer-extra-fields', cutomer_views.CompanyTypeFieldsView, basename='customer-extra-fields')
router.register(r'customer-field-options', cutomer_views.CustomerFieldOptionsView, basename='customer-field-options')
router.register(r'customers', cutomer_views.CustomersView, basename='customers')

router.register(r'region', location_views.RegionViewSet, basename='regions')
router.register(r'district', location_views.DistrictViewSet, basename='districts')
router.register(r'county', location_views.CountyViewSet, basename='counties')
router.register(r'subcounty', location_views.SubCountyViewSet, basename='subcounties')
router.register(r'parish', location_views.ParishViewSet, basename='parishes')
router.register(r'village', location_views.VillageViewSet, basename='villages')
router.register(r'customer-address', location_views.CustomerAddressViewSet, basename='customer-address')
router.register(r'company-address', location_views.CompanyAddressViewSet, basename='company-address')

router.register(r'system-components',systemrights_views.SystemComponentsView, basename='system-components')
router.register(r'users', user_views.UserView, basename='users')
router.register(r'departments', user_views.DepartmentView, basename='departments')
router.register(r'job-titles', user_views.JobTitleView, basename='job-titles')
router.register(r'staff', user_views.StaffView, basename='staff')

router.register(r'contacts', user_views.ContactsView, basename='contacts')
router.register(r'sms-apps', user_views.SMSAPIAppsView, basename='sms-apps')
router.register(r'user-groups',systemrights_views.UserGroupView, basename='user-groups')
router.register(r'branches', companies_views.CompanyBranchView, basename='branches')
router.register(r'company-coas', ledgers_views.AccountsChartView, basename='company-coas')
router.register(r'currencies', ledgers_views.CurrenciesView, basename='company-coas')
router.register(r'bank-accounts', ledgers_views.BankAccountView, basename='bank-accounts')
router.register(r'cash-accounts', ledgers_views.CashAccountView, basename='cash-accounts')
router.register(r'safe-accounts', ledgers_views.SafeAccountView, basename='safe-accounts')
router.register(r'mm-accounts', ledgers_views.MobileMoneyAccountView, basename='mm-accounts')
router.register(r'cash-transfers', ledgers_views.CashTransfersView, basename='cash-transfers')
router.register(r'my-transfers', ledgers_views.MyTransfersView, basename='my-transfers')
router.register(r'pending-expense-ledger-transactions', ledgers_views.PendingExpenseLedgerTransactionsViewset, basename='pending-expense-ledger-transactions')
router.register(r'advanced-ledger-transactions', ledgers_views.AdvanvedTransactionsView, basename='advanced-ledger-transactions')

router.register(r'suppliers', ledgers_views.SuppliersView, basename='suppliers')
router.register(r'creditors', ledgers_views.CreditorsView, basename='creditors')
router.register(r'creditorsupplies', ledgers_views.CreditorSuppliesView, basename='creditorsupplies')
router.register(r'expense-items', ledgers_views.ExpenseItemsViewSet, basename='expense-items')

router.register(r'inv-product-categories', inventory_views.ProductCategoriesViewSet, basename='inv-product-categories')
router.register(r'inv-product-tags', inventory_views.ProductTagsViewSet, basename='inv-product-tags')
router.register(r'inv-products', inventory_views.ProductsViewSet, basename='inv-products')
router.register(r'inv-product-variations', inventory_views.ProductVariationsViewSet, basename='inv-product-variations')
router.register(r'product-pricing', inventory_views.ProductPricingViewSet, basename='product-pricing')
router.register(r'pos-product-tags', pos_views.PosProductTagsViewSet, basename='pos-product-tags')
router.register(r'service-categories', service_views.ServiceCategoriesViewSet, basename='service-categories')
router.register(r'service-tags', service_views.ServiceTagsViewSet, basename='service-tags')
router.register(r'services', service_views.ServicesViewSet, basename='services')
router.register(r'service-variations', service_views.ServiceVariationsViewSet, basename='service-variations')


router.register(r'staff-contracts', hr_views.StaffContractsViewSet, basename='staff-contracts')
router.register(r'salaries', hr_views.SalariesViewSet, basename='salaries')

router.register(r'staff-deductions', hr_views.StaffDeductionsViewSet, basename='staff-deductions')
router.register(r'salary-payments', hr_views.SalaryPaymentsViewSet, basename='salary-payments')

# Inventory   
router.register(r'pumps', inventory_views.PumpsView, basename='pumps')
router.register(r'pump-assignments', inventory_views.PumpAssignmentsView, basename='pump-assignments')
router.register(r'pump-products', inventory_views.PumpProductsView, basename='pump-products')
router.register(r'pump-readings', inventory_views.PumpReadingsView, basename='pump-readings')
router.register(r'shifts', inventory_views.ShiftsView, basename='shifts')


router.register(r'stock-list', inventory_views.StocksViewSet, basename='stock-list')
router.register(r'purchase-requisition-list', inventory_views.PurchaseRequisitionsViewSet, basename='purchase-requisition-list')
router.register(r'order-list', inventory_views.OrdersViewSet, basename='order-list')
router.register(r'invoice-list', inventory_views.InvoicesViewSet, basename='invoice-list')


#router.register(r'sale-requisition-list', inventory_views.SaleRequisitionsViewSet, basename='sale-requisition-list')

#router.register(r'seasons', inventory_views.OrganisationSeasonViewSet, basename='organisation-season')


urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token-auth/', user_views.RestAPIJWT.as_view()), 
    path('api/obtain-token/', user_views.ObtainAPITokenView.as_view()), 
    path('api/logout/', user_views.LogOutUserView.as_view()), 
    path('api/user-visits/', user_views.UserVisitsAPIView.as_view()),
    path('api/user-likes/', user_views.UserLikesAPIView.as_view()),
    path('api/register-user/', user_views.RegisterUserApiView.as_view()),
    path('api/reset-password/', user_views.ResetPasswordView.as_view()),

    path('api/system-rights/', systemrights_views.SystemRightView.as_view()),
    path('api/company-type-components/',systemrights_views.CompanyTypeComponentsView.as_view()),
    path('api/company-components/', systemrights_views.CompanyComponentView.as_view()),
    path('api/company-rights/', systemrights_views.CompanyRightsApiView.as_view()),
    path('api/group-rights/', systemrights_views.GroupRightsView.as_view()),
    path('api/company-general-settings/', companies_views.GeneralSettingsView.as_view()),
    path('api/switch-company/', companies_views.SwitchCompany.as_view()),
    path('api/refresh-coa/', companies_views.RefreshCOAsView.as_view()),
    path('api/ledger-transaction-list/', ledgers_views.LedgerTransactionsListView.as_view()),
    path('api/ledger-transactional-charts/', ledgers_views.LedgerTransactionalChartsView.as_view()),
    path('api/income-ledger-transactions/', ledgers_views.IncomeLedgerTransactionsView.as_view()),
    path('api/post-ledger-transations/', ledgers_views.PostLedgerTransationView.as_view()),
    path('api/expense-ledger-transactions/', ledgers_views.ExpenseLedgerTransactionsView.as_view()),
   
    path('api/trial-balance/', report_views.TrialBalanceView.as_view()),
    path('api/income-statement/', report_views.IncomeStatementView.as_view()),
    path('api/balance-sheet/', report_views.BalanceSheetView.as_view()),
    
    path('api/pos-shops/', pos_views.PosShopsView.as_view()),
    path('api/pos-products/', pos_views.PosProductsView.as_view()),
    path('api/pos-product-categories/', pos_views.PosProductCategoriesView.as_view()),

    path('api/stock-taking/', inventory_views.StockTakingView.as_view()),
    
    # Pump Updates
    path('api/capture-pump-readings/', inventory_views.CapturePumpReadingView.as_view()),
    path('api/pump-summarry/', inventory_views.PumpSummaryView.as_view()),
    path('api/branch-summary/', inventory_views.BranchSummaryView.as_view()),
    path('api/cash-payments/', inventory_views.CashTransationView.as_view()),
    path('api/generate-payroll/', hr_views.GeneratePayrollView.as_view()),
    path('api/capture-salaries/', hr_views.CaptureSalriesView.as_view()),
    path('api/staff-salary-balance/', hr_views.StaffSalaryBalanceView.as_view()),
    path('api/switch-branch/', companies_views.SwitchBranch.as_view()), 
    
]

