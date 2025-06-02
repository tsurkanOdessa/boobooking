from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from config import settings


class CustomPagination(PageNumberPagination):
    page_size = getattr(settings, 'REST_FRAMEWORK', {}).get('PAGE_SIZE', 4)
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page_size': self.get_page_size(self.request),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
