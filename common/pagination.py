# common/pagination.py
from rest_framework.pagination import PageNumberPagination
from common.responses import APIResponse
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return APIResponse(
            success=True,
            message="List fetched successfully",
            data={
                "items": data,
                "meta": {
                    "count": self.page.paginator.count,
                    "page": self.page.number,
                    "page_size": self.page.paginator.per_page,
                    "total_pages": self.page.paginator.num_pages
                }
            },
            status=200
        )
