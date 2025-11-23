from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status, viewsets
from performances.models import Performance
from performances.serializers import PerformanceSerializer
from rest_framework.decorators import api_view


class PerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        return Performance.objects.filter(profile=self.request.user)


@api_view(["GET"])
def get_user_performances(_request: Request, user_id: int) -> Response:
    all_user_performances = Performance.objects.filter(profile__id=user_id)

    serializer = PerformanceSerializer(all_user_performances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
