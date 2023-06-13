from rest_framework.pagination import PageNumberPagination


class PageLimitPagination(PageNumberPagination):
    """Обычный пагинатор, но с limit"""
    page_size_query_param = 'limit'
