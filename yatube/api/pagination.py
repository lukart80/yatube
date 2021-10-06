from rest_framework import pagination
from rest_framework.response import Response


class PostPagination(pagination.LimitOffsetPagination):
    """Паджинатор для постов."""
    def get_paginated_response(self, data):
        if self.limit and self.offset is None:
            return Response(data)
        return Response({
            'count': self.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data}
        )
