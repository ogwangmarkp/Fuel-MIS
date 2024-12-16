from rest_framework.pagination import PageNumberPagination, _positive_int


class CustomPageNumberPagination(PageNumberPagination):
    """ A custom DRF paginator class
    """
    # Client can control the page using this query parameter.
    page_query_param = 'page'
    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = 'page_size'

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = 10000

    def get_page_size(self, request):
        
        if self.page_size_query_param in request.query_params:
            try:
                return _positive_int(
                    request.query_params[self.page_size_query_param],
                    strict=True,
                    cutoff=self.max_page_size
                )
            except (KeyError, ValueError):
                pass

        return self.page_size