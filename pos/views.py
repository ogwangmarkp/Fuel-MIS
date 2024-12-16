from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from inventory.models import ProductVariation,ProductCategory,ProductTag,ProductAssignedTag
from inventory.serializers import ProductTagSerializer,ProductCategorySerializer, ProductVariationSerializer
from companies.models import Company
from .serializers import  CompanySerializer
from rest_framework.permissions import AllowAny

class PosProductTagsViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = ProductTagSerializer
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend, )
    search_fields = ('tag_name', )

    def get_queryset(self):
        return ProductTag.objects.filter(**{"deleted": False}).order_by('tag_name')

class PosProductCategoriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        company_id = self.request.GET.get("company",None)
        categories = ProductCategory.objects.filter(**{"company__id":company_id,"deleted": False}).order_by("category_name")
        json_categories = ProductCategorySerializer(categories,many=True).data
       
        return Response({"results":json_categories,"count":len(json_categories)})
    
class PosProductsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        tags = self.request.GET.get("tags",None)
        search = self.request.GET.get("search",None)
        shops  = self.request.GET.get("shops",None)
        categories = self.request.GET.get("categories",None)
        
        filter_query = {}
        id = self.request.GET.get("id",None)
        if id:
             filter_query['id'] = id
        else:
            if tags:
                tags  = list(tags.split(','))
                product_ids = []
                if search:
                    product_ids =  ProductAssignedTag.objects.filter(tag__tag_name__icontains=search,tag__id__in=tags).values_list('product__id', flat=True)
                else:
                    product_ids =  ProductAssignedTag.objects.filter(tag__id__in=tags).values_list('product__id', flat=True)

                filter_query['product__id__in'] = product_ids
            
            if categories:
                categories  = list(categories.split(','))
                filter_query['product__category__id__in'] = categories
            
            if shops:
                filter_query['product__company__id__in'] = list(shops.split(','))

        products = []
        if search:
            products   = ProductVariation.objects.filter(
                Q(product__category__category_name__icontains=search) |
                Q(variation_name__icontains=search)| 
                Q(product__product_name__icontains=search),
                **filter_query
            ).order_by("variation_name")
        else:
            products = ProductVariation.objects.filter(**filter_query).order_by("variation_name")

        count      = len(products)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        products = paginator.paginate_queryset(products, request)
        json_products = ProductVariationSerializer(products,many=True).data
       
        return Response({"results":json_products,"count":count})

class PosShopsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        tags = self.request.GET.get("tags",None)
        id = self.request.GET.get("id",None)
        filter_query = {}
        if id:
             filter_query['id'] = id
        else:
            if tags:
                tags  = list(tags.split(','))
                company_ids =  ProductAssignedTag.objects.filter(tag__id__in=tags).values_list('product__company__id', flat=True)
                filter_query['id__in'] = company_ids
        companies = Company.objects.filter(**filter_query).order_by("name")
        count      = len(companies)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        companies = paginator.paginate_queryset(companies, request)
        json_companies = CompanySerializer(companies,many=True).data
       
        return Response({"results":json_companies,"count":count})

class StockTakingView(APIView):

    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        tags = self.request.GET.get("tags",None)
        search = self.request.GET.get("search",None)
        shops  = self.request.GET.get("shops",None)
        categories = self.request.GET.get("categories",None)
        
        filter_query = {}
        
        products = ProductVariation.objects.filter(**filter_query).order_by("variation_name")

        count      = len(products)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        products = paginator.paginate_queryset(products, request)
        json_products = ProductVariationSerializer(products,many=True).data
       
        return Response({"results":json_products,"count":count})
    
''' class PosShopsView(APIView):
    
    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        categories = self.request.GET.get("categories",None)
        category_ids = []
        filter_query = {}
        if categories:
            categories  = list(categories.split(','))
            for category_id in categories:
                category_ids = category_ids + self.get_children_cat_ids(category_id)
        
            filter_query['product__category__id__in'] = category_ids
            products   = ProductVariation.objects.filter(**filter_query).order_by("name")
            
        count      = len(products)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        products = paginator.paginate_queryset(products, request)
        json_products = PosProductVariationsSerializer(products,many=True).data
       
        return Response({"results":json_products,"count":count})
    
    def get_children_cat_ids(self,parent_id):
        data = []
        category_ids = ProductCategory.objects.filter(parent_component=parent_id).values_list('id', flat=True)
        if(len(category_ids) > 0):
            for category_id in category_ids:
                children_ids = self.get_children_cat_ids(category_id)
                if(len(children_ids) > 0):
                    for children_id in children_ids:
                        children2 = self.get_children_cat_ids(children_id)
                        data.append(children_id)
                        data = data + children2
                if(len(children_ids) < 1):
                    data.append(category_id)
        return data
   

class PosProductsView(APIView):
    
    def get(self, request):
        count      = 0
        page_size  = self.request.GET.get("page_size",20)
        categories = self.request.GET.get("categories",None)
        companies  = self.request.GET.get("companies",None)
        category_ids = []
        filter_query = {}
        if categories:
            categories  = list(categories.split(','))
            for category_id in categories:
                category_ids = category_ids + self.get_children_cat_ids(category_id)
        
            filter_query['product__category__id__in'] = category_ids
        
        if companies:
            filter_query['product__company__id__in'] = list(companies.split(','))

        products   = ProductVariation.objects.filter(**filter_query).order_by("name")
        count      = len(products)
        paginator  = PageNumberPagination()
        paginator.page_size = page_size
        products = paginator.paginate_queryset(products, request)
        json_products = PosProductVariationsSerializer(products,many=True).data
       
        return Response({"results":json_products,"count":count})
    
    def get_children_cat_ids(self,parent_id):
        data = []
        category_ids = ProductCategory.objects.filter(parent_component=parent_id).values_list('id', flat=True)
        if(len(category_ids) > 0):
            for category_id in category_ids:
                children_ids = self.get_children_cat_ids(category_id)
                if(len(children_ids) > 0):
                    for children_id in children_ids:
                        children2 = self.get_children_cat_ids(children_id)
                        data.append(children_id)
                        data = data + children2
                if(len(children_ids) < 1):
                    data.append(category_id)
        return data
'''