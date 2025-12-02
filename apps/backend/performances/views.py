from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from performances.models import Performance
from performances.serializers import PerformanceSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = Performance.objects.filter(profile=self.request.user)
            return queryset
        return Performance.objects.none()


@api_view(["GET"])
def get_user_performances(_request: Request, user_id: int) -> Response:
    all_user_performances = Performance.objects.filter(profile__id=user_id)

    serializer = PerformanceSerializer(all_user_performances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
